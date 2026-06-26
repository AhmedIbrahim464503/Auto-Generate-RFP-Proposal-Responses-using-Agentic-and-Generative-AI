from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ContactSchema(BaseModel):
    organization: Optional[str] = None
    department: Optional[str] = None
    primary_contact: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class AnalysisMetadataResponse(BaseModel):
    document_title: Optional[str] = None
    client_name: Optional[str] = None
    project_name: Optional[str] = None
    rfp_number: Optional[str] = None
    issue_date: Optional[str] = None
    submission_deadline: Optional[str] = None
    contacts: List[ContactSchema] = []
    normalized_submission_deadline: Optional[datetime] = None
    normalized_question_deadline: Optional[datetime] = None

class SectionResponse(BaseModel):
    id: str
    parent_id: Optional[str] = None
    title: str
    content: Optional[str] = None
    classification: Optional[str] = None
    confidence: float
    page_start: int
    page_end: int
    hierarchy_level: int

class StructureTreeResponse(BaseModel):
    title: str
    classification: Optional[str] = None
    confidence: float
    page_start: int
    page_end: int
    subsections: List['StructureTreeResponse'] = []

# Rebuild forward ref
StructureTreeResponse.model_rebuild()

class QualityReportResponse(BaseModel):
    quality_score: float
    quality_report: Optional[str] = None
    missing_pages_detected: bool
    unreadable_sections_detected: bool
    corrupted_content_detected: bool
    duplicate_sections_detected: bool
    empty_sections_detected: bool

class AnalysisStatusResponse(BaseModel):
    success: bool
    rfp_document_id: str
    analyzed_at: datetime
    inference_metadata: Dict[str, Any]
