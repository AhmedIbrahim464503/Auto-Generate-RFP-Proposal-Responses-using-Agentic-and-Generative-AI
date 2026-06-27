from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WorkflowExecutionBase(BaseModel):
    workflow_name: str
    proposal_id: str
    status: str
    current_node: str
    state: Dict[str, Any]
    error_message: Optional[str] = None

class WorkflowExecutionResponse(WorkflowExecutionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowCheckpointResponse(BaseModel):
    id: str
    execution_id: str
    node_name: str
    state: Dict[str, Any]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowEventResponse(BaseModel):
    id: str
    execution_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowMetricResponse(BaseModel):
    id: str
    execution_id: str
    node_name: str
    duration_seconds: float
    tokens_used: int
    cost: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowApprovalGateResponse(BaseModel):
    id: str
    execution_id: str
    node_name: str
    status: str
    requested_at: datetime
    decided_at: Optional[datetime] = None
    decision_payload: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

class StartWorkflowRequest(BaseModel):
    workflow_name: str = "Proposal Lifecycle Workflow"
    proposal_id: str

class ResumeWorkflowRequest(BaseModel):
    action: str  # approve, reject, revise, override
    payload: Optional[Dict[str, Any]] = None

class RollbackWorkflowRequest(BaseModel):
    target_node: str

# Typed GraphState Pydantic structure for LangGraph workflow execution
class WorkflowGraphState(BaseModel):
    workflow_metadata: Dict[str, Any] = Field(default_factory=dict)
    proposal_metadata: Dict[str, Any] = Field(default_factory=dict)
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    requirements: List[Dict[str, Any]] = Field(default_factory=list)
    department_reviews: List[Dict[str, Any]] = Field(default_factory=list)
    qualification_results: Dict[str, Any] = Field(default_factory=dict)
    planning_outputs: Dict[str, Any] = Field(default_factory=dict)
    knowledge_retrieval_results: List[Dict[str, Any]] = Field(default_factory=list)
    generated_sections: List[Dict[str, Any]] = Field(default_factory=list)
    review_findings: List[Dict[str, Any]] = Field(default_factory=list)
    human_approvals: List[Dict[str, Any]] = Field(default_factory=list)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    audit_references: List[Dict[str, Any]] = Field(default_factory=list)
    current_node: str = "init"
    previous_node: Optional[str] = None
    execution_status: str = "running"  # running, paused, completed, failed
    errors: List[str] = Field(default_factory=list)
    retry_counts: Dict[str, int] = Field(default_factory=dict)
