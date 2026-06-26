import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.knowledge import KnowledgeAsset, KnowledgeChunk, SearchLog, GovernanceRecord
from backend.app.services.knowledge_engine import knowledge_engine_service
from backend.app.schemas.knowledge import (
    KnowledgeAssetCreate,
    KnowledgeAssetResponse,
    KnowledgeAssetUpdateRequest,
    KnowledgeChunkResponse,
    GovernanceRecordResponse,
    SearchLogResponse,
    KnowledgeSearchResponse,
    SearchResultItem,
    ChunkSearchCitation
)

router = APIRouter()

def serialize_asset(asset: KnowledgeAsset) -> KnowledgeAssetResponse:
    chunks = []
    for c in asset.chunks:
        chunks.append(KnowledgeChunkResponse(
            id=str(c.id),
            parent_asset_id=str(c.parent_asset_id),
            parent_section=c.parent_section,
            chunk_index=c.chunk_index,
            content=c.content,
            metadata=json.loads(c.metadata_json) if c.metadata_json else {},
            source_location=c.source_location,
            embedding_vector=json.loads(c.embedding_vector) if c.embedding_vector else None
        ))

    records = []
    for r in asset.governance_records:
        records.append(GovernanceRecordResponse(
            id=str(r.id),
            asset_id=str(r.asset_id),
            action=r.action,
            actor=r.actor,
            comments=r.comments,
            payload=json.loads(r.payload_json) if r.payload_json else {},
            timestamp=r.timestamp
        ))

    tags_list = []
    if asset.tags:
        try:
            tags_list = json.loads(asset.tags)
        except Exception:
            tags_list = [asset.tags]

    return KnowledgeAssetResponse(
        id=str(asset.id),
        title=asset.title,
        content=asset.content,
        asset_type=asset.asset_type,
        version=asset.version,
        owner=asset.owner,
        department=asset.department,
        tags=tags_list,
        source=asset.source,
        approval_status=asset.approval_status,
        review_date=asset.review_date,
        expiration_date=asset.expiration_date,
        quality_score=asset.quality_score,
        usage_count=asset.usage_count,
        last_retrieved_at=asset.last_retrieved_at,
        trust_score=asset.trust_score,
        embedding_version=asset.embedding_version,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        is_deleted=asset.is_deleted,
        chunks=chunks,
        governance_records=records
    )

@router.post("/upload", response_model=KnowledgeAssetResponse)
def upload_asset(payload: KnowledgeAssetCreate, db: Session = Depends(get_db)):
    asset = KnowledgeAsset(
        title=payload.title,
        content=payload.content,
        asset_type=payload.asset_type,
        owner=payload.owner,
        department=payload.department,
        tags=json.dumps(payload.tags) if payload.tags else "[]",
        source=payload.source,
        approval_status="DRAFT",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Log Governance UPLOAD
    gov = GovernanceRecord(
        asset_id=asset.id,
        action="UPLOAD",
        actor=payload.owner or "Capture Manager",
        comments="Knowledge Asset uploaded successfully. Waiting for indexation.",
        payload_json=json.dumps({"asset_type": payload.asset_type}),
        timestamp=datetime.utcnow()
    )
    db.add(gov)
    db.commit()
    db.refresh(asset)

    # Trigger indexing immediately
    knowledge_engine_service.index_asset(db, asset.id, actor=asset.owner)

    return serialize_asset(asset)

@router.post("/index", response_model=KnowledgeAssetResponse)
def index_asset(id: str, db: Session = Depends(get_db)):
    try:
        asset = knowledge_engine_service.index_asset(db, id)
        return serialize_asset(asset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[KnowledgeAssetResponse])
def get_assets(
    asset_type: Optional[str] = None,
    department: Optional[str] = None,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeAsset).filter(KnowledgeAsset.is_deleted == False)
    if asset_type:
        query = query.filter(KnowledgeAsset.asset_type == asset_type)
    if department:
        query = query.filter(KnowledgeAsset.department == department)
    if approval_status:
        query = query.filter(KnowledgeAsset.approval_status == approval_status)
    
    return [serialize_asset(a) for a in query.all()]

@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    query: str,
    top_k: Optional[int] = 5,
    confidence_threshold: Optional[float] = 0.0,
    department: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = {}
    if department:
        filters["department"] = department
    if asset_type:
        filters["asset_type"] = asset_type

    start_time = datetime.utcnow()
    results = knowledge_engine_service.hybrid_search(
        db,
        query,
        top_k=top_k,
        filters=filters if filters else None,
        confidence_threshold=confidence_threshold
    )
    latency = (datetime.utcnow() - start_time).total_seconds() * 1000.0

    output_results = []
    for r in results:
        cit = r["citation"]
        output_results.append(SearchResultItem(
            content=r["content"],
            citation=ChunkSearchCitation(
                chunk_id=cit["chunk_id"],
                parent_asset_id=cit["parent_asset_id"],
                document_title=cit["document_title"],
                page=cit["page"],
                section=cit["section"],
                paragraph=cit["paragraph"],
                similarity_score=cit["similarity_score"],
                rerank_score=cit["rerank_score"],
                embedding_version=cit["embedding_version"],
                knowledge_version=cit["knowledge_version"]
            )
        ))

    return KnowledgeSearchResponse(
        query=query,
        results=output_results,
        latency_ms=latency
    )

@router.get("/chunks", response_model=List[KnowledgeChunkResponse])
def get_chunks(asset_id: str, db: Session = Depends(get_db)):
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.parent_asset_id == asset_id).all()
    out = []
    for c in chunks:
        out.append(KnowledgeChunkResponse(
            id=str(c.id),
            parent_asset_id=str(c.parent_asset_id),
            parent_section=c.parent_section,
            chunk_index=c.chunk_index,
            content=c.content,
            metadata=json.loads(c.metadata_json) if c.metadata_json else {},
            source_location=c.source_location,
            embedding_vector=json.loads(c.embedding_vector) if c.embedding_vector else None
        ))
    return out

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    assets = db.query(KnowledgeAsset.asset_type).filter(KnowledgeAsset.is_deleted == False).distinct().all()
    return [a[0] for a in assets if a[0]]

@router.get("/history", response_model=List[SearchLogResponse])
def get_history(db: Session = Depends(get_db)):
    logs = db.query(SearchLog).order_by(SearchLog.timestamp.desc()).limit(50).all()
    out = []
    for log in logs:
        out.append(SearchLogResponse(
            id=str(log.id),
            query_text=log.query_text,
            filters=json.loads(log.filters_json) if log.filters_json else {},
            results=json.loads(log.results_json) if log.results_json else [],
            latency_ms=log.latency_ms,
            timestamp=log.timestamp
        ))
    return out

@router.get("/{id}", response_model=KnowledgeAssetResponse)
def get_asset(id: str, db: Session = Depends(get_db)):
    asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == id, KnowledgeAsset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return serialize_asset(asset)

@router.post("/{id}/update", response_model=KnowledgeAssetResponse)
def update_asset(id: str, payload: KnowledgeAssetUpdateRequest, db: Session = Depends(get_db)):
    asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == id, KnowledgeAsset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    updated_fields = {}
    if payload.title is not None:
        asset.title = payload.title
        updated_fields["title"] = payload.title
    if payload.content is not None:
        asset.content = payload.content
        updated_fields["content"] = "updated"
    if payload.asset_type is not None:
        asset.asset_type = payload.asset_type
        updated_fields["asset_type"] = payload.asset_type
    if payload.owner is not None:
        asset.owner = payload.owner
        updated_fields["owner"] = payload.owner
    if payload.department is not None:
        asset.department = payload.department
        updated_fields["department"] = payload.department
    if payload.tags is not None:
        asset.tags = json.dumps(payload.tags)
        updated_fields["tags"] = payload.tags
    if payload.approval_status is not None:
        asset.approval_status = payload.approval_status
        updated_fields["approval_status"] = payload.approval_status
    if payload.review_date is not None:
        asset.review_date = payload.review_date
    if payload.expiration_date is not None:
        asset.expiration_date = payload.expiration_date
    if payload.quality_score is not None:
        asset.quality_score = payload.quality_score
    if payload.trust_score is not None:
        asset.trust_score = payload.trust_score

    asset.updated_at = datetime.utcnow()

    # Log Governance EDIT
    gov = GovernanceRecord(
        asset_id=asset.id,
        action="APPROVE" if payload.approval_status == "APPROVED" else "EDIT",
        actor="Capture Manager",
        comments=f"Governance details updated: {list(updated_fields.keys())}",
        payload_json=json.dumps(updated_fields),
        timestamp=datetime.utcnow()
    )
    db.add(gov)
    db.commit()
    db.refresh(asset)
    return serialize_asset(asset)
