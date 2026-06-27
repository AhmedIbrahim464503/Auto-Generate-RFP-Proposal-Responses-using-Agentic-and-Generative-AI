import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base_class import Base

class WorkflowExecution(Base):
    __tablename__ = "workflow_execution"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_name: Mapped[str] = mapped_column(String(100), nullable=False)
    proposal_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="running")  # running, paused, completed, failed
    current_node: Mapped[str] = mapped_column(String(100), default="init")
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoint"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), nullable=False)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class WorkflowEvent(Base):
    __tablename__ = "workflow_event"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # WorkflowStarted, NodeStarted, NodeCompleted, NodeFailed, CheckpointSaved, HumanApprovalRequested, HumanApproved, WorkflowCompleted, WorkflowFailed
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class WorkflowMetric(Base):
    __tablename__ = "workflow_metric"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), nullable=False)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class WorkflowApprovalGate(Base):
    __tablename__ = "workflow_approval_gate"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), nullable=False)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    decision_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
