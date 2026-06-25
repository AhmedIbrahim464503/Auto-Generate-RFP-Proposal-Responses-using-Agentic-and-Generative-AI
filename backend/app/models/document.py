import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class RFPDocument(Base):
    __tablename__ = "rfp_document"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="rfp_documents")
    requirements = relationship("Requirement", back_populates="rfp_document", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirement"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)  # technical, legal, financial, etc.
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    rfp_document = relationship("RFPDocument", back_populates="requirements")
    deliverables = relationship("Deliverable", back_populates="requirement", cascade="all, delete-orphan")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="requirement", cascade="all, delete-orphan")
    submission_instructions = relationship("SubmissionInstruction", back_populates="requirement", cascade="all, delete-orphan")
    compliance_items = relationship("ComplianceItem", back_populates="requirement")


class Deliverable(Base):
    __tablename__ = "deliverable"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[str] = mapped_column(String(100), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="deliverables")


class EvaluationCriteria(Base):
    __tablename__ = "evaluation_criteria"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement.id"), nullable=False)
    criteria_text: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[str] = mapped_column(String(50), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="evaluation_criteria")


class SubmissionInstruction(Base):
    __tablename__ = "submission_instruction"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement.id"), nullable=False)
    instruction_text: Mapped[str] = mapped_column(Text, nullable=False)
    format_type: Mapped[str] = mapped_column(String(100), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="submission_instructions")
