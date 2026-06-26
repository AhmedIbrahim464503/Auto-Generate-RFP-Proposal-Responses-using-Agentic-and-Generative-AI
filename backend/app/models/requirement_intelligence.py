import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class ComplianceObligation(Base):
    __tablename__ = "compliance_obligation"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Unknown")  # Unknown, Compliant, Non-Compliant
    department_owner: Mapped[str] = mapped_column(String(100), nullable=True)
    evidence_required: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=True)
    blocking: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class RFPRisk(Base):
    __tablename__ = "rfp_risk"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(36), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=True)  # High, Medium, Low
    likelihood: Mapped[str] = mapped_column(String(50), nullable=True)
    business_impact: Mapped[str] = mapped_column(Text, nullable=True)
    mitigation_suggestion: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class RFPAssumption(Base):
    __tablename__ = "rfp_assumption"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)  # Business, Technical, Operational, Contractual
    is_explicit: Mapped[bool] = mapped_column(Boolean, default=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class ClarificationQuestion(Base):
    __tablename__ = "clarification_question"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(36), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_recipient: Mapped[str] = mapped_column(String(100), nullable=True)
    business_impact: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edge"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rfp_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("rfp_document.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)  # requirement, deliverable, risk, compliance_obligation, assumption, clarification_question, department
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)  # triggers, mitigates, requires, belongs_to, addresses


class RequirementAssignment(Base):
    __tablename__ = "requirement_assignment"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement.id"), nullable=False)
    department_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Technical, Legal, Finance, Operations, Proposal Management, Executive Approval
