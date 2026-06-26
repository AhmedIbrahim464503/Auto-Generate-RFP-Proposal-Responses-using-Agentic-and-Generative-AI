import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class QualificationDecision(Base):
    __tablename__ = "qualification_decision"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, APPROVED, OVERRIDDEN, RE_ANALYSIS_REQUESTED
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)  # GO, GO_WITH_CONDITIONS, ESCALATE, NO_GO
    final_decision: Mapped[str] = mapped_column(String(50), nullable=True)  # GO, GO_WITH_CONDITIONS, ESCALATE, NO_GO
    decision_by: Mapped[str] = mapped_column(String(100), nullable=True)
    decision_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=True)
    positive_factors: Mapped[str] = mapped_column(Text, nullable=True)
    negative_factors: Mapped[str] = mapped_column(Text, nullable=True)
    blocking_issues: Mapped[str] = mapped_column(Text, nullable=True)
    mitigating_factors: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[str] = mapped_column(Text, nullable=True)
    escalation_requirements: Mapped[str] = mapped_column(Text, nullable=True)
    outstanding_clarifications: Mapped[str] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str] = mapped_column(Text, nullable=True)
    business_impact: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Scoring
    opportunity_score: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_win_probability: Mapped[float] = mapped_column(Float, default=0.0)
    win_probability_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Metadata
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)
    rule_version: Mapped[str] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="qualification_decision")
    scoring_breakdowns = relationship("QualificationScoringBreakdown", back_populates="qualification", cascade="all, delete-orphan")
    comments = relationship("QualificationExecutiveComment", back_populates="qualification", cascade="all, delete-orphan")


class QualificationScoringBreakdown(Base):
    __tablename__ = "qualification_scoring_breakdown"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qualification_id: Mapped[str] = mapped_column(String(36), ForeignKey("qualification_decision.id"), nullable=False)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False)  # strategic_fit, capability, financial, risk, compliance, opportunity, relationship, complexity
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    qualification = relationship("QualificationDecision", back_populates="scoring_breakdowns")


class QualificationDecisionHistory(Base):
    __tablename__ = "qualification_decision_history"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # GENERATE, APPROVE, REJECT, OVERRIDE, RE_ANALYSIS_REQUESTED, WEIGHT_ADJUSTED
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QualificationExecutiveComment(Base):
    __tablename__ = "qualification_executive_comment"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qualification_id: Mapped[str] = mapped_column(String(36), ForeignKey("qualification_decision.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    qualification = relationship("QualificationDecision", back_populates="comments")


class QualificationRule(Base):
    __tablename__ = "qualification_rule"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(100), default="global")  # allows future regional/business unit scopes
    rules_payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON weights, thresholds, blockers, etc.
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
