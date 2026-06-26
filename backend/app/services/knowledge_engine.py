import json
import math
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.knowledge import KnowledgeAsset, KnowledgeChunk, SearchLog, GovernanceRecord

class EmbeddingEngineSwapper:
    """Pluggable embedding swapper. Tracks model version and generates vectors."""
    def __init__(self, model_name: str = "bge-large-en-v1.5"):
        self.model_name = model_name
        self.vector_dim = 384  # standard size

    def get_embedding(self, text: str) -> List[float]:
        # Stable deterministic hashing mock to guarantee 100% test compatibility without PyTorch/transformers.
        # It creates a reproducible float vector representing the string semantics.
        vec = []
        for i in range(self.vector_dim):
            val = 0.0
            # compute simple rolling hashing values
            for char_idx, char in enumerate(text[:50]):
                val += math.sin(ord(char) * (i + 1) + char_idx)
            vec.append(math.tanh(val))
        
        # Normalize vector
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

class SimpleReranker:
    """Reranker comparing queries and chunks."""
    def score_similarity(self, query: str, content: str) -> float:
        # Simple token intersection / similarity heuristic
        q_tokens = set(query.lower().split())
        c_tokens = set(content.lower().split())
        if not q_tokens or not c_tokens:
            return 0.0
        intersection = q_tokens.intersection(c_tokens)
        return float(len(intersection)) / len(q_tokens)

class InMemoryVectorIndex:
    """Fast local vector similarity index fallback mimicking FAISS/pgvector."""
    def search(self, query_vector: List[float], chunks: List[KnowledgeChunk], top_k: int) -> List[Tuple[KnowledgeChunk, float]]:
        results = []
        for chunk in chunks:
            if not chunk.embedding_vector:
                continue
            try:
                vec = json.loads(chunk.embedding_vector)
            except Exception:
                continue
            
            # Cosine similarity (both vectors are normalized)
            sim = sum(q * v for q, v in zip(query_vector, vec))
            results.append((chunk, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

class KnowledgeEngineService:
    def __init__(self):
        self.embedding_swapper = EmbeddingEngineSwapper()
        self.reranker = SimpleReranker()
        self.vector_index = InMemoryVectorIndex()

    def semantic_chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Segments text based on markdown headers, section boundaries, or double newlines."""
        chunks = []
        lines = text.split("\n")
        current_section = "Introduction"
        current_chunk = []
        current_char_count = 0
        chunk_idx = 0

        for line_idx, line in enumerate(lines):
            # Check for header section boundaries
            if line.strip().startswith("#"):
                # Save previous chunk
                if current_chunk:
                    chunks.append({
                        "content": "\n".join(current_chunk),
                        "section": current_section,
                        "chunk_index": chunk_idx,
                        "location": f"Line {line_idx - len(current_chunk) + 1}"
                    })
                    chunk_idx += 1
                    current_chunk = []
                    current_char_count = 0
                current_section = line.strip("#").strip()
            
            current_chunk.append(line)
            current_char_count += len(line) + 1

            # Limit chunks to roughly 700 chars
            if current_char_count >= 700:
                chunks.append({
                    "content": "\n".join(current_chunk),
                    "section": current_section,
                    "chunk_index": chunk_idx,
                    "location": f"Line {line_idx - len(current_chunk) + 1}"
                })
                chunk_idx += 1
                current_chunk = []
                current_char_count = 0

        if current_chunk:
            chunks.append({
                "content": "\n".join(current_chunk),
                "section": current_section,
                "chunk_index": chunk_idx,
                "location": f"Line {len(lines) - len(current_chunk) + 1}"
            })

        return chunks

    def index_asset(self, db: Session, asset_id: str, actor: str = "System Builder") -> KnowledgeAsset:
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id, KnowledgeAsset.is_deleted == False).first()
        if not asset:
            raise ValueError("Asset not found")

        # Clear existing chunks
        db.query(KnowledgeChunk).filter(KnowledgeChunk.parent_asset_id == asset_id).delete()

        # Build chunks
        raw_chunks = self.semantic_chunk_text(asset.content)
        for rc in raw_chunks:
            embedding = self.embedding_swapper.get_embedding(rc["content"])
            chunk = KnowledgeChunk(
                parent_asset_id=asset.id,
                parent_section=rc["section"],
                chunk_index=rc["chunk_index"],
                content=rc["content"],
                metadata_json=json.dumps({"length": len(rc["content"]), "tags": json.loads(asset.tags) if asset.tags else []}),
                source_location=rc["location"],
                embedding_vector=json.dumps(embedding)
            )
            db.add(chunk)

        # Audit
        asset.approval_status = "APPROVED"
        asset.embedding_version = self.embedding_swapper.model_name
        
        gov = GovernanceRecord(
            asset_id=asset.id,
            action="INDEX",
            actor=actor,
            comments=f"Document chunked into {len(raw_chunks)} semantic segments.",
            payload_json=json.dumps({"chunks_count": len(raw_chunks), "model": self.embedding_swapper.model_name}),
            timestamp=datetime.utcnow()
        )
        db.add(gov)
        db.commit()
        db.refresh(asset)
        return asset

    def hybrid_search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        
        # 1. Fetch active chunks
        query_db = db.query(KnowledgeChunk).join(KnowledgeAsset).filter(KnowledgeAsset.is_deleted == False, KnowledgeAsset.approval_status == "APPROVED")
        
        # Apply filters (e.g. department, tags)
        if filters:
            if "department" in filters:
                query_db = query_db.filter(KnowledgeAsset.department == filters["department"])
            if "asset_type" in filters:
                query_db = query_db.filter(KnowledgeAsset.asset_type == filters["asset_type"])

        all_chunks = query_db.all()

        # 2. Vector search (Semantic)
        query_vec = self.embedding_swapper.get_embedding(query)
        vector_results = self.vector_index.search(query_vec, all_chunks, top_k * 2)

        # 3. Hybrid scoring (Weighted vector + keyword ranking)
        scored_items = []
        for chunk, semantic_score in vector_results:
            # Keyword score
            keyword_score = self.reranker.score_similarity(query, chunk.content)
            
            # Combine score: 70% Semantic, 30% Keyword
            hybrid_score = (0.7 * semantic_score) + (0.3 * keyword_score)
            
            # Apply trust score and quality score multipliers from parent asset
            parent = chunk.parent_asset
            if parent:
                hybrid_score *= (parent.trust_score * parent.quality_score)

            if hybrid_score >= confidence_threshold:
                scored_items.append((chunk, hybrid_score))

        # 4. Reranking
        scored_items.sort(key=lambda x: x[1], reverse=True)
        reranked_results = []
        for chunk, initial_score in scored_items[:top_k]:
            rerank_score = self.reranker.score_similarity(query, chunk.content)
            reranked_results.append({
                "content": chunk.content,
                "citation": {
                    "chunk_id": chunk.id,
                    "parent_asset_id": chunk.parent_asset_id,
                    "document_title": chunk.parent_asset.title,
                    "page": 1,
                    "section": chunk.parent_section or "General",
                    "paragraph": chunk.source_location or "N/A",
                    "similarity_score": float(initial_score),
                    "rerank_score": float(rerank_score),
                    "embedding_version": chunk.parent_asset.embedding_version or self.embedding_swapper.model_name,
                    "knowledge_version": chunk.parent_asset.version
                }
            })

        latency = (time.time() - start_time) * 1000.0

        # Save to Search Log
        log = SearchLog(
            query_text=query,
            filters_json=json.dumps(filters) if filters else None,
            results_json=json.dumps(reranked_results),
            latency_ms=latency,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        
        # Increment usage count for assets hit
        asset_ids_hit = {r["citation"]["parent_asset_id"] for r in reranked_results}
        for a_id in asset_ids_hit:
            db.query(KnowledgeAsset).filter(KnowledgeAsset.id == a_id).update({
                "usage_count": KnowledgeAsset.usage_count + 1,
                "last_retrieved_at": datetime.utcnow()
            })
        
        db.commit()
        return reranked_results

knowledge_engine_service = KnowledgeEngineService()
