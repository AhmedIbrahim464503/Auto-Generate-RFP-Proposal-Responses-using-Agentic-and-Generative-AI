import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base_class import Base

class KnowledgeAsset(Base):
    __tablename__ = "knowledge_asset"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=True)  # historical_proposal, policy, case_study, etc.
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    owner: Mapped[str] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    tags: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list
    source: Mapped[str] = mapped_column(String(255), default="Upload")
    approval_status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, APPROVED, REJECTED, EXPIRED
    review_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_retrieved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    trust_score: Mapped[float] = mapped_column(Float, default=1.0)
    embedding_version: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    chunks: Mapped[list["KnowledgeChunk"]] = relationship("KnowledgeChunk", back_populates="parent_asset", cascade="all, delete-orphan")
    governance_records: Mapped[list["GovernanceRecord"]] = relationship("GovernanceRecord", back_populates="asset", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunk"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_asset.id"), nullable=False)
    parent_section: Mapped[str] = mapped_column(String(255), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    source_location: Mapped[str] = mapped_column(String(255), nullable=True)  # Page 5, Paragraph 2
    embedding_vector: Mapped[str] = mapped_column(Text, nullable=True)  # JSON representation of float list

    # Relationships
    parent_asset: Mapped[KnowledgeAsset] = relationship("KnowledgeAsset", back_populates="chunks")


class SearchLog(Base):
    __tablename__ = "search_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text: Mapped[str] = mapped_column(String(500), nullable=False)
    filters_json: Mapped[str] = mapped_column(Text, nullable=True)
    results_json: Mapped[str] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GovernanceRecord(Base):
    __tablename__ = "governance_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_asset.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # UPLOAD, INDEX, APPROVE, EXPIRE, REINDEX
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset: Mapped[KnowledgeAsset] = relationship("KnowledgeAsset", back_populates="governance_records")
