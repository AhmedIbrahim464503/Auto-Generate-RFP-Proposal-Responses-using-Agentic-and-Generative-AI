import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class GeneratedSection(Base):
    __tablename__ = "generated_section"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    proposal_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_section.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tone_style: Mapped[str] = mapped_column(String(50), default="Professional")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)
    prompt_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    model_version: Mapped[str] = mapped_column(String(50), default="gemini-2.5-flash")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    citations: Mapped[list["ProposalCitation"]] = relationship("ProposalCitation", back_populates="generated_section", cascade="all, delete-orphan")
    evidence_links: Mapped[list["ProposalEvidenceLink"]] = relationship("ProposalEvidenceLink", back_populates="generated_section", cascade="all, delete-orphan")


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_plan.id"), nullable=False)
    proposal_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposal_section.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # GENERATE, REGENERATE, EDIT
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    content_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProposalCitation(Base):
    __tablename__ = "proposal_citation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    generated_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_section.id", ondelete="CASCADE"), nullable=False)
    paragraph_index: Mapped[int] = mapped_column(Integer, nullable=False)
    knowledge_asset_id: Mapped[str] = mapped_column(String(36), nullable=True)
    knowledge_chunk_id: Mapped[str] = mapped_column(String(36), nullable=True)
    requirement_id: Mapped[str] = mapped_column(String(36), nullable=True)
    compliance_item_id: Mapped[str] = mapped_column(String(36), nullable=True)
    source_title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_location: Mapped[str] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Relationships
    generated_section: Mapped[GeneratedSection] = relationship("GeneratedSection", back_populates="citations")


class ProposalEvidenceLink(Base):
    __tablename__ = "proposal_evidence_link"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    generated_section_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_section.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)  # requirement, knowledge, review
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)

    # Relationships
    generated_section: Mapped[GeneratedSection] = relationship("GeneratedSection", back_populates="evidence_links")
