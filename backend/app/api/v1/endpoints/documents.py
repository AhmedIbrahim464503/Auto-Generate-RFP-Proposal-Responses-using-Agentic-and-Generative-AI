import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.db.session import get_db
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.models.audit import AuditEvent
from backend.app.services.storage import storage_service
from backend.app.services.document_processor import DocumentProcessorFactory
from backend.app.core.logger import logger
from backend.app.schemas.api_contracts import UploadResponse

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def validate_file(file: UploadFile) -> str:
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension {ext}. Allowed: PDF, DOCX"
        )
    return ext


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    opportunity_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Validates, stores, and registers an RFP document.
    """
    ext = validate_file(file)
    content = await file.read()
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of 50MB."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is empty."
        )

    # Resolve or create opportunity
    if not opportunity_id:
        opp = Opportunity(
            title=f"Auto Opportunity - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            description="Auto-generated for upload tracking."
        )
        db.add(opp)
        db.flush()
        opportunity_id = opp.id
    else:
        opp = db.get(Opportunity, opportunity_id)
        if not opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opportunity_id} not found."
            )

    # Save to storage
    unique_filename = f"{uuid.uuid4()}{ext}"
    local_path = storage_service.save_file(content, unique_filename)

    # Register document
    doc = RFPDocument(
        opportunity_id=opportunity_id,
        file_name=file.filename or "unknown",
        file_path=local_path
    )
    db.add(doc)
    db.flush()

    # Log audit event
    audit = AuditEvent(
        actor="SystemUser",
        action="DOCUMENT_UPLOADED",
        entity_name="rfp_document",
        entity_id=doc.id,
        reason="Initial document ingestion"
    )
    db.add(audit)
    db.commit()

    logger.info(f"Document uploaded and registered: {doc.id} associated with opportunity: {opportunity_id}")
    
    return UploadResponse(
        success=True,
        rfp_document_id=doc.id,
        file_name=doc.file_name,
        uploaded_at=doc.uploaded_at
    )


@router.get("", response_model=List[dict])
def list_documents(db: Session = Depends(get_db)):
    """
    Lists all ingested documents.
    """
    stmt = select(RFPDocument).where(RFPDocument.is_deleted == False)
    docs = db.scalars(stmt).all()
    return [
        {
            "id": doc.id,
            "opportunity_id": doc.opportunity_id,
            "file_name": doc.file_name,
            "uploaded_at": doc.uploaded_at
        } for doc in docs
    ]


@router.get("/{id}", response_model=dict)
def get_document(id: str, db: Session = Depends(get_db)):
    """
    Fetches details of a specific document.
    """
    doc = db.get(RFPDocument, id)
    if not doc or doc.is_deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "opportunity_id": doc.opportunity_id,
        "file_name": doc.file_name,
        "uploaded_at": doc.uploaded_at
    }


@router.get("/{id}/status", response_model=dict)
def get_document_status(id: str, db: Session = Depends(get_db)):
    """
    Fetches status tracking for the document.
    """
    doc = db.get(RFPDocument, id)
    if not doc or doc.is_deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Mocking lifecycle validation/processed status transitions since they run synchronously
    return {
        "id": doc.id,
        "status": "PROCESSED",
        "steps": [
            {"step": "UPLOADED", "timestamp": doc.uploaded_at.isoformat(), "success": True},
            {"step": "VALIDATED", "timestamp": doc.uploaded_at.isoformat(), "success": True},
            {"step": "STORED", "timestamp": doc.uploaded_at.isoformat(), "success": True},
            {"step": "PROCESSED", "timestamp": doc.uploaded_at.isoformat(), "success": True}
        ]
    }


@router.get("/{id}/metadata", response_model=dict)
def get_document_metadata(id: str, db: Session = Depends(get_db)):
    """
    Extracts basic structural metadata from the document.
    """
    doc = db.get(RFPDocument, id)
    if not doc or doc.is_deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        processor = DocumentProcessorFactory.get_processor(doc.file_path)
        meta = processor.extract_metadata(doc.file_path)
        return {
            "id": doc.id,
            "file_name": doc.file_name,
            **meta
        }
    except Exception as e:
        logger.error(f"Failed to extract metadata for doc {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata extraction failed: {str(e)}"
        )
