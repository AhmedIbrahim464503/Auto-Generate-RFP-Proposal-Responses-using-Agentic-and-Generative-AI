import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.db.session import get_db
from backend.app.models.document import RFPDocument
from backend.app.models.analysis import DocumentSection, RFPMetadata
from backend.app.models.audit import AuditEvent
from backend.app.services.document_processor import DocumentProcessorFactory
from backend.app.services.ai_engine import ai_engine_service, SectionStructure
from backend.app.core.logger import logger
from backend.app.schemas.analysis import (
    AnalysisStatusResponse,
    StructureTreeResponse,
    SectionResponse,
    AnalysisMetadataResponse,
    QualityReportResponse
)

router = APIRouter()

def parse_iso_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None


@router.post("/{id}/analyze", response_model=AnalysisStatusResponse)
def analyze_document(id: str, db: Session = Depends(get_db)):
    """
    Invokes Gemini 2.5 Flash to segment and extract metadata/structure.
    """
    doc = db.get(RFPDocument, id)
    if not doc or doc.is_deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Read document text content
    t0 = time.time()
    try:
        processor = DocumentProcessorFactory.get_processor(doc.file_path)
        doc_text = processor.extract_text(doc.file_path)
    except Exception as e:
        logger.error(f"Failed to read file text for doc {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to read file text content")

    # 2. Invoke AI Engine for structural segmentation
    sections: List[SectionStructure] = ai_engine_service.analyze_document_structure(doc_text)
    
    # 3. Invoke AI Engine for metadata & quality check
    meta = ai_engine_service.analyze_document_metadata(doc_text)
    
    latency_ms = (time.time() - t0) * 1000

    # 4. Clear any previous analysis to avoid duplicates
    db.query(DocumentSection).filter(DocumentSection.rfp_document_id == id).delete()
    db.query(RFPMetadata).filter(RFPMetadata.rfp_document_id == id).delete()

    # 5. Persist section hierarchy recursive function
    def save_section(sec: SectionStructure, parent_id: str = None, level: int = 1) -> str:
        db_sec = DocumentSection(
            rfp_document_id=id,
            parent_id=parent_id,
            title=sec.title,
            content=sec.content,
            classification=sec.classification,
            confidence=sec.confidence,
            page_start=sec.page_start,
            page_end=sec.page_end,
            hierarchy_level=level
        )
        db.add(db_sec)
        db.flush()
        
        for sub in sec.subsections:
            save_section(sub, parent_id=db_sec.id, level=level + 1)
        
        return db_sec.id

    for section in sections:
        save_section(section, parent_id=None, level=1)

    # 6. Persist Metadata
    db_meta = RFPMetadata(
        rfp_document_id=id,
        document_title=meta.document_title,
        client_name=meta.client_name,
        project_name=meta.project_name,
        rfp_number=meta.rfp_number,
        issue_date=meta.issue_date,
        submission_deadline=meta.submission_deadline,
        contact_info=json.dumps([c.model_dump() for c in meta.contacts]),
        normalized_submission_deadline=parse_iso_date(meta.submission_deadline),
        normalized_question_deadline=parse_iso_date(meta.question_deadline) if meta.question_deadline else None,
        quality_score=meta.quality_score,
        quality_report=json.dumps({
            "missing_pages": meta.missing_pages_detected,
            "unreadable_sections": meta.unreadable_sections_detected,
            "corrupted_content": meta.corrupted_content_detected,
            "duplicate_sections": meta.duplicate_sections_detected,
            "empty_sections": meta.empty_sections_detected
        }),
        inference_time_ms=latency_ms
    )
    db.add(db_meta)

    # Log audit event
    audit = AuditEvent(
        actor="AIEngine",
        action="DOCUMENT_ANALYZED",
        entity_name="rfp_document",
        entity_id=id,
        reason="Extracted document structure and quality score"
    )
    db.add(audit)
    db.commit()

    return AnalysisStatusResponse(
        success=True,
        rfp_document_id=id,
        analyzed_at=datetime.utcnow(),
        inference_metadata={
            "model": db_meta.model_name,
            "latency_ms": latency_ms,
            "prompt_version": db_meta.prompt_version
        }
    )


@router.get("/{id}/structure", response_model=List[StructureTreeResponse])
def get_document_structure(id: str, db: Session = Depends(get_db)):
    """
    Returns hierarchical document section structure.
    """
    stmt = select(DocumentSection).where(DocumentSection.rfp_document_id == id, DocumentSection.is_deleted == False)
    sections = db.scalars(stmt).all()
    if not sections:
        raise HTTPException(status_code=404, detail="No structure found. Run analyze first.")

    # Convert flat list into tree representation
    nodes = {str(sec.id): {
        "title": sec.title,
        "classification": sec.classification,
        "confidence": sec.confidence,
        "page_start": sec.page_start,
        "page_end": sec.page_end,
        "subsections": []
    } for sec in sections}

    roots = []
    for sec in sections:
        node = nodes[str(sec.id)]
        if sec.parent_id:
            parent = nodes.get(str(sec.parent_id))
            if parent:
                parent["subsections"].append(node)
        else:
            roots.append(node)

    return [StructureTreeResponse(**r) for r in roots]


@router.get("/{id}/sections", response_model=List[SectionResponse])
def list_document_sections(id: str, db: Session = Depends(get_db)):
    """
    Returns flat list of document sections.
    """
    stmt = select(DocumentSection).where(DocumentSection.rfp_document_id == id, DocumentSection.is_deleted == False)
    sections = db.scalars(stmt).all()
    return [
        SectionResponse(
            id=str(sec.id),
            parent_id=str(sec.parent_id) if sec.parent_id else None,
            title=sec.title,
            content=sec.content,
            classification=sec.classification,
            confidence=sec.confidence,
            page_start=sec.page_start,
            page_end=sec.page_end,
            hierarchy_level=sec.hierarchy_level
        ) for sec in sections
    ]


@router.get("/{id}/metadata", response_model=AnalysisMetadataResponse)
def get_analysis_metadata(id: str, db: Session = Depends(get_db)):
    """
    Returns detailed extracted metadata (dates, contacts, clients).
    """
    stmt = select(RFPMetadata).where(RFPMetadata.rfp_document_id == id)
    meta = db.scalar(stmt)
    if not meta:
        raise HTTPException(status_code=404, detail="No metadata found. Run analyze first.")

    contacts = []
    if meta.contact_info:
        try:
            contacts = json.loads(meta.contact_info)
        except Exception:
            pass

    return AnalysisMetadataResponse(
        document_title=meta.document_title,
        client_name=meta.client_name,
        project_name=meta.project_name,
        rfp_number=meta.rfp_number,
        issue_date=meta.issue_date,
        submission_deadline=meta.submission_deadline,
        contacts=contacts,
        normalized_submission_deadline=meta.normalized_submission_deadline,
        normalized_question_deadline=meta.normalized_question_deadline
    )


@router.get("/{id}/quality", response_model=QualityReportResponse)
def get_document_quality(id: str, db: Session = Depends(get_db)):
    """
    Returns the document quality report details.
    """
    stmt = select(RFPMetadata).where(RFPMetadata.rfp_document_id == id)
    meta = db.scalar(stmt)
    if not meta:
        raise HTTPException(status_code=404, detail="No quality report found. Run analyze first.")

    q_details = {
        "missing_pages": False,
        "unreadable_sections": False,
        "corrupted_content": False,
        "duplicate_sections": False,
        "empty_sections": False
    }
    if meta.quality_report:
        try:
            q_details = json.loads(meta.quality_report)
        except Exception:
            pass

    return QualityReportResponse(
        quality_score=meta.quality_score,
        quality_report=meta.quality_report,
        missing_pages_detected=q_details.get("missing_pages", False),
        unreadable_sections_detected=q_details.get("unreadable_sections", False),
        corrupted_content_detected=q_details.get("corrupted_content", False),
        duplicate_sections_detected=q_details.get("duplicate_sections", False),
        empty_sections_detected=q_details.get("empty_sections", False)
    )


@router.get("/{id}/analysis", response_model=dict)
def get_complete_analysis_summary(id: str, db: Session = Depends(get_db)):
    """
    Fetches full analysis metadata, quality summary, and flat sections counts.
    """
    meta = db.scalar(select(RFPMetadata).where(RFPMetadata.rfp_document_id == id))
    sections_count = db.query(DocumentSection).filter(DocumentSection.rfp_document_id == id).count()
    
    if not meta:
        raise HTTPException(status_code=404, detail="No analysis logs found. Run analyze first.")

    return {
        "rfp_document_id": id,
        "title": meta.document_title,
        "client": meta.client_name,
        "quality_score": meta.quality_score,
        "sections_count": sections_count,
        "analyzed_at": meta.created_at
    }
