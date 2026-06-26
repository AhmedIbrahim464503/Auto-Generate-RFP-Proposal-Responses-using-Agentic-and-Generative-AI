import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class DocumentSection(Base):
    __tablename__ = "document_section"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    parent_id: Mapped[str] = mapped_column(String(36), nullable=True)  # self-referential parent id
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    classification: Mapped[str] = mapped_column(String(100), nullable=True)  # Introduction, Scope, Legal, etc.
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    page_start: Mapped[int] = mapped_column(Integer, default=1)
    page_end: Mapped[int] = mapped_column(Integer, default=1)
    hierarchy_level: Mapped[int] = mapped_column(Integer, default=1)  # 1 for Section, 2 for Subsection, etc.
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class RFPMetadata(Base):
    __tablename__ = "rfp_metadata"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    
    # AI Extracted details
    document_title: Mapped[str] = mapped_column(String(255), nullable=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=True)
    rfp_number: Mapped[str] = mapped_column(String(100), nullable=True)
    issue_date: Mapped[str] = mapped_column(String(100), nullable=True)
    submission_deadline: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_info: Mapped[str] = mapped_column(Text, nullable=True)  # JSON or text blob
    
    # Normalized deadlines
    normalized_submission_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    normalized_question_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Document Quality Reports
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)
    quality_report: Mapped[str] = mapped_column(Text, nullable=True)  # JSON structured string
    
    # Inference Metadata
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-2.5-flash")
    prompt_version: Mapped[str] = mapped_column(String(50), default="1.0")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    inference_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
