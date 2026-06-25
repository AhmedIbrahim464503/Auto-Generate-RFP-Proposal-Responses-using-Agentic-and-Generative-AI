import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base_class import Base

class KnowledgeAsset(Base):
    __tablename__ = "knowledge_asset"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=True)  # historical_proposal, product_wiki, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class SearchResult(Base):
    __tablename__ = "search_result"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text: Mapped[str] = mapped_column(String(500), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    retrieved_content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SystemConfiguration(Base):
    __tablename__ = "system_configuration"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    config_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
