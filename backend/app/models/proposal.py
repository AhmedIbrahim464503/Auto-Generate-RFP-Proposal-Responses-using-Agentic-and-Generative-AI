import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class ProposalPlan(Base):
    __tablename__ = "proposal_plan"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="proposal_plan")
    sections = relationship("ProposalSection", back_populates="proposal_plan", cascade="all, delete-orphan")


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
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # COMPLIANT, NON_COMPLIANT, PARTIALLY_COMPLIANT
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    compliance_matrix = relationship("ComplianceMatrix", back_populates="items")
    requirement = relationship("Requirement", back_populates="compliance_items")


class ProposalSection(Base):
    __tablename__ = "proposal_section"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, COMPLETED, REVIEWED
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    proposal_plan = relationship("ProposalPlan", back_populates="sections")
