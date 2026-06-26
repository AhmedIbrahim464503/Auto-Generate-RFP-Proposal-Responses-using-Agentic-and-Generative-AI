import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class ProposalReviewSession(Base):
    __tablename__ = "proposal_review_session"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="AWAIT_HUMAN_REVIEW")  # PASS, PASS_WITH_REVISIONS, BLOCKED, ESCALATE, REGENERATE, AWAIT_HUMAN_REVIEW
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    meta_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    findings: Mapped[list["ProposalReviewFinding"]] = relationship("ProposalReviewFinding", back_populates="session", cascade="all, delete-orphan")
    scores: Mapped[list["ProposalReviewScore"]] = relationship("ProposalReviewScore", back_populates="session", cascade="all, delete-orphan")
    audits: Mapped[list["ProposalReviewAudit"]] = relationship("ProposalReviewAudit", back_populates="session", cascade="all, delete-orphan")


class ProposalReviewFinding(Base):
    __tablename__ = "proposal_review_finding"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_review_session.id", ondelete="CASCADE"), nullable=False)
    generated_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_section.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # compliance, citation, grammar, readability, consistency, security, risk
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # info, warning, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped[ProposalReviewSession] = relationship("ProposalReviewSession", back_populates="findings")


class ProposalReviewScore(Base):
    __tablename__ = "proposal_review_score"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_review_session.id", ondelete="CASCADE"), nullable=False)
    generated_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_section.id", ondelete="CASCADE"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped[ProposalReviewSession] = relationship("ProposalReviewSession", back_populates="scores")


class ProposalReviewWorkflow(Base):
    __tablename__ = "proposal_review_workflow"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    stages: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON array of workflow steps/agents
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProposalReviewAudit(Base):
    __tablename__ = "proposal_review_audit"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_review_session.id", ondelete="CASCADE"), nullable=False)
    generated_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_section.id", ondelete="CASCADE"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # approve, reject, override, comment, lock, unlock
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped[ProposalReviewSession] = relationship("ProposalReviewSession", back_populates="audits")
