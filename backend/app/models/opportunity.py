import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class Opportunity(Base):
    __tablename__ = "opportunity"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    rfp_documents = relationship("RFPDocument", back_populates="opportunity", cascade="all, delete-orphan")
    reviews = relationship("FinancialReview", back_populates="opportunity")
    legal_reviews = relationship("LegalReview", back_populates="opportunity")
    ops_reviews = relationship("OperationsReview", back_populates="opportunity")
    tech_reviews = relationship("TechnicalReview", back_populates="opportunity")
    qualification_decision = relationship("QualificationDecision", back_populates="opportunity", uselist=False)
    proposal_plan = relationship("ProposalPlan", back_populates="opportunity", uselist=False)
    approval_gates = relationship("ApprovalGate", back_populates="opportunity")
