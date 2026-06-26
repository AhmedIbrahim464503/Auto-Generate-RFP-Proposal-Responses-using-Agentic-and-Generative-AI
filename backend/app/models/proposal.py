import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class ProposalPlan(Base):
    __tablename__ = "proposal_plan"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    client: Mapped[str] = mapped_column(String(255), nullable=True)
    rfp_name: Mapped[str] = mapped_column(String(255), nullable=True)
    proposal_type: Mapped[str] = mapped_column(String(100), nullable=True)
    submission_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    estimated_duration_days: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    estimated_effort_hours: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    complexity: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    priority: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    required_departments: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    executive_sponsor: Mapped[str] = mapped_column(String(100), nullable=True)
    proposal_owner: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, LOCKED, APPROVED
    version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    planning_notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="proposal_plan")
    sections = relationship("ProposalSection", back_populates="proposal_plan", cascade="all, delete-orphan")
    tasks = relationship("ProposalTask", back_populates="proposal_plan", cascade="all, delete-orphan")
    milestones = relationship("ProposalMilestone", back_populates="proposal_plan", cascade="all, delete-orphan")
    required_documents = relationship("RequiredDocument", back_populates="proposal_plan", cascade="all, delete-orphan")
    clarification_requests = relationship("ClarificationRequest", back_populates="proposal_plan", cascade="all, delete-orphan")
    history_records = relationship("PlanningHistory", back_populates="proposal_plan", cascade="all, delete-orphan")


class ProposalSection(Base):
    __tablename__ = "proposal_section"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, COMPLETED, REVIEWED
    
    # Ownership and Planning details
    owner: Mapped[str] = mapped_column(String(100), nullable=True)
    reviewer: Mapped[str] = mapped_column(String(100), nullable=True)
    approver: Mapped[str] = mapped_column(String(100), nullable=True)
    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    dependencies: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string list of Section IDs
    priority: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    risk_level: Mapped[str] = mapped_column(String(50), nullable=True, default="Low")
    is_human_editable: Mapped[bool] = mapped_column(Boolean, default=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="sections")
    compliance_items = relationship("ComplianceItem", back_populates="proposal_section")


class ComplianceMatrix(Base):
    __tablename__ = "compliance_matrix"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    items = relationship("ComplianceItem", back_populates="compliance_matrix", cascade="all, delete-orphan")


class ComplianceItem(Base):
    __tablename__ = "compliance_item"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_matrix_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_matrix.id"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement.id"), nullable=False)
    proposal_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_section.id"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Unknown")  # COMPLIANT, NON_COMPLIANT, PARTIALLY_COMPLIANT, Unknown
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    
    responsible_department: Mapped[str] = mapped_column(String(100), nullable=True)
    responsible_owner: Mapped[str] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    evidence_required: Mapped[str] = mapped_column(Text, nullable=True)
    source_page: Mapped[int] = mapped_column(Integer, nullable=True)
    source_paragraph: Mapped[str] = mapped_column(Text, nullable=True)
    risk_if_missing: Mapped[str] = mapped_column(Text, nullable=True)
    dependencies: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    reviewer: Mapped[str] = mapped_column(String(100), nullable=True)
    approval_status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    traceability_links: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    comments: Mapped[str] = mapped_column(Text, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    compliance_matrix = relationship("ComplianceMatrix", back_populates="items")
    requirement = relationship("Requirement", back_populates="compliance_items")
    proposal_section = relationship("ProposalSection", back_populates="compliance_items")


class ProposalTask(Base):
    __tablename__ = "proposal_task"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    parent_task_id: Mapped[str] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="TODO")  # TODO, IN_PROGRESS, REVIEW, DONE
    dependencies: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string list of task IDs
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_critical_path: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="tasks")


class ProposalMilestone(Base):
    __tablename__ = "proposal_milestone"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="milestones")


class RequiredDocument(Base):
    __tablename__ = "required_document"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="MISSING")  # MISSING, REQUESTED, RECEIVED, APPROVED, REJECTED, EXPIRED
    required_by_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="required_documents")


class ClarificationRequest(Base):
    __tablename__ = "clarification_request"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    related_requirement_id: Mapped[str] = mapped_column(String(36), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=True, default="Medium")
    owner: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, SUBMITTED, RESOLVED
    client_response: Mapped[str] = mapped_column(Text, nullable=True)
    impact: Mapped[str] = mapped_column(Text, nullable=True)
    resolution: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="clarification_requests")


class PlanningHistory(Base):
    __tablename__ = "planning_history"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # GENERATE, EDIT, LOCK, UNLOCK, APPROVE, REJECT
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="history_records")
