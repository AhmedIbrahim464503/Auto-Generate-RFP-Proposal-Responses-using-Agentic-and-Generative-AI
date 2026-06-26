import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base_class import Base

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(100), nullable=False)  # gemini, openai, claude, local
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)  # gemini-2.5-flash, etc.
    api_endpoint: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    latency: Mapped[float] = mapped_column(Float, default=0.0)
    availability: Mapped[float] = mapped_column(Float, default=1.0)
    cost_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AgentRegistry(Base):
    __tablename__ = "agent_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    supported_tools: Mapped[list] = mapped_column(JSON, default=list)
    supported_models: Mapped[list] = mapped_column(JSON, default=list)
    prompt_versions: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    owner: Mapped[str] = mapped_column(String(100), nullable=True)
    health_status: Mapped[str] = mapped_column(String(50), default="healthy")
    approval_status: Mapped[str] = mapped_column(String(50), default="approved")
    deprecation_status: Mapped[bool] = mapped_column(Boolean, default=False)

class PromptRegistry(Base):
    __tablename__ = "prompt_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), nullable=True)
    prompt_name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    developer_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    user_template: Mapped[str] = mapped_column(Text, nullable=True)
    output_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    rollback_version: Mapped[str] = mapped_column(String(50), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ToolRegistry(Base):
    __tablename__ = "tool_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    tool_type: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

class WorkflowRegistry(Base):
    __tablename__ = "workflow_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)

class CapabilityRegistry(Base):
    __tablename__ = "capability_registry"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    agent_id: Mapped[str] = mapped_column(String(36), nullable=False)

class AgentMemory(Base):
    __tablename__ = "agent_memory"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)  # short_term, long_term, cache
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentMetric(Base):
    __tablename__ = "agent_metric"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), nullable=False)
    execution_id: Mapped[str] = mapped_column(String(36), nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="success")
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    human_override: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ExplainabilityRecord(Base):
    __tablename__ = "explainability_record"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), nullable=True)
    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    retrieved_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    rules_used: Mapped[dict] = mapped_column(JSON, default=dict)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    output_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AIConfig(Base):
    __tablename__ = "ai_config"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

class GovernancePolicy(Base):
    __tablename__ = "governance_policy"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rules_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

