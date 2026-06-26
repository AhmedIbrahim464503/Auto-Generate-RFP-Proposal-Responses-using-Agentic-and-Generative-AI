## Chunking Strategy (Phase 9)
- **Semantic Chunking**: Scans text for markdown headers, section boundaries, or double newlines, keeping logical text groups intact under parent headings.
- **Chunk Size**: Target limits are roughly 700 characters.

## Embedding Engine Swapper
- **Model Swapping**: Decoupled interface supporting Sentence Transformers, BGE, Jina, and Nomic vectorizers.
- **Deterministic Mock**: Deterministic mock math hashing fallback for local offline testing (384-dimensional normalized vectors).
- **Embedding Versioning**: Tracked on the `KnowledgeAsset` record.

## Hybrid Search & Vector Database
- **Primary DB**: `pgvector` for production PostgreSQL.
- **Fallback DB**: Memory-based vector cosine-similarity index for local runs and unit testing.
- **Hybrid Scoring**: Combines semantic cosine similarity (70% weight) with keyword token intersections (30% weight) and scales by asset trust and quality indexes.

## Reranking & Citations
- **Reranker**: Pluggable Cross-Encoder interface calculating secondary relevancy.
- **Citation Builder**: Preserves traceability to the parent asset, version, section, page, and chunk index.

