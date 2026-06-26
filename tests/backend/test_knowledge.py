import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.knowledge import KnowledgeAsset, KnowledgeChunk, SearchLog, GovernanceRecord
from backend.app.services.knowledge_engine import knowledge_engine_service

def test_semantic_chunking():
    text = "# Section 1\nThis is text under section 1.\nIt has multiple sentences.\n# Section 2\nThis is some text under section 2."
    chunks = knowledge_engine_service.semantic_chunk_text(text)
    
    assert len(chunks) >= 2
    assert chunks[0]["section"] == "Section 1"
    assert chunks[1]["section"] == "Section 2"
    assert "Section 1" in chunks[0]["content"]
    assert "Section 2" in chunks[1]["content"]

def test_embedding_swapper():
    engine = knowledge_engine_service.embedding_swapper
    v1 = engine.get_embedding("Test content one")
    v2 = engine.get_embedding("Test content one")
    v3 = engine.get_embedding("Completely different string structure")

    assert len(v1) == 384
    assert v1 == v2
    assert v1 != v3
    # Check normalization
    norm = sum(x * x for x in v1)
    assert abs(norm - 1.0) < 1e-5

def test_reranker_and_hybrid():
    q = "SOC2 security audit"
    c1 = "We run annual SOC2 security audits for operations."
    c2 = "The cafeteria menu serves delicious lasagna."
    
    s1 = knowledge_engine_service.reranker.score_similarity(q, c1)
    s2 = knowledge_engine_service.reranker.score_similarity(q, c2)
    
    assert s1 > s2
    assert s1 > 0.0
    assert s2 == 0.0

def test_knowledge_api_workflow(client: TestClient, test_db):
    # 1. Upload a Knowledge Asset
    asset_data = {
        "title": "Corporate Compliance Standards",
        "content": "# Compliance Overview\nWe follow strict corporate rules.\n# Legal Framework\nAll contracts must go through reviews.",
        "asset_type": "policy",
        "owner": "Legal Lead",
        "department": "Legal",
        "tags": ["corporate", "legal"],
        "source": "Upload"
    }

    res_upload = client.post("/api/v1/knowledge/upload", json=asset_data)
    assert res_upload.status_code == 200
    res_json = res_upload.json()
    assert res_json["title"] == "Corporate Compliance Standards"
    assert res_json["approval_status"] == "APPROVED"  # Auto indexes and approves
    assert len(res_json["chunks"]) >= 2
    
    asset_id = res_json["id"]

    # 2. Get active assets
    res_list = client.get("/api/v1/knowledge")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Search knowledge semantically
    res_search = client.get("/api/v1/knowledge/search?query=corporate rules&top_k=2")
    assert res_search.status_code == 200
    search_json = res_search.json()
    assert search_json["query"] == "corporate rules"
    assert len(search_json["results"]) >= 1
    assert "Compliance Overview" in [r["citation"]["section"] for r in search_json["results"]]

    # 4. View Chunks
    res_chunks = client.get(f"/api/v1/knowledge/chunks?asset_id={asset_id}")
    assert res_chunks.status_code == 200
    assert len(res_chunks.json()) >= 2

    # 5. View Categories
    res_cats = client.get("/api/v1/knowledge/categories")
    assert res_cats.status_code == 200
    assert "policy" in res_cats.json()

    # 6. View Governance records
    res_asset = client.get(f"/api/v1/knowledge/{asset_id}")
    assert res_asset.status_code == 200
    assert len(res_asset.json()["governance_records"]) >= 2  # Upload + Index

    # 7. Update status to EXPIRED (Governance)
    res_update = client.post(f"/api/v1/knowledge/{asset_id}/update", json={"approval_status": "EXPIRED"})
    assert res_update.status_code == 200
    assert res_update.json()["approval_status"] == "EXPIRED"

    # 8. View Search history log
    res_history = client.get("/api/v1/knowledge/history")
    assert res_history.status_code == 200
    assert len(res_history.json()) >= 1
    assert res_history.json()[0]["query_text"] == "corporate rules"
