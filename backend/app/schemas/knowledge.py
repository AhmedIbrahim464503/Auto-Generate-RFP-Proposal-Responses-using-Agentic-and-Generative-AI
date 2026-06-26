from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class KnowledgeAssetCreate(BaseModel):
    title: str
    content: str
    asset_type: Optional[str] = "policy"
    owner: Optional[str] = "Capture Manager"
    department: Optional[str] = "General"
    tags: Optional[List[str]] = []
    source: Optional[str] = "Upload"

class KnowledgeAssetUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    asset_type: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    approval_status: Optional[str] = None
    review_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    quality_score: Optional[float] = None
    trust_score: Optional[float] = None

class KnowledgeChunkResponse(BaseModel):
    id: str
    parent_asset_id: str
    parent_section: Optional[str] = None
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = {}
    source_location: Optional[str] = None
    embedding_vector: Optional[List[float]] = None

class GovernanceRecordResponse(BaseModel):
    id: str
    asset_id: str
    action: str
    actor: str
    comments: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime

class KnowledgeAssetResponse(BaseModel):
    id: str
    title: str
    content: str
    asset_type: Optional[str] = None
    version: str
    owner: Optional[str] = None
    department: Optional[str] = None
    tags: List[str] = []
    source: str
    approval_status: str
    review_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    quality_score: float
    usage_count: int
    last_retrieved_at: Optional[datetime] = None
    trust_score: float
    embedding_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    chunks: List[KnowledgeChunkResponse] = []
    governance_records: List[GovernanceRecordResponse] = []

class SearchLogResponse(BaseModel):
    id: str
    query_text: str
    filters: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None
    latency_ms: float
    timestamp: datetime

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    confidence_threshold: Optional[float] = 0.0
    filters: Optional[Dict[str, Any]] = None

class ChunkSearchCitation(BaseModel):
    chunk_id: str
    parent_asset_id: str
    document_title: str
    page: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[str] = None
    similarity_score: float
    rerank_score: float
    embedding_version: str
    knowledge_version: str

class SearchResultItem(BaseModel):
    content: str
    citation: ChunkSearchCitation

class KnowledgeSearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    latency_ms: float
