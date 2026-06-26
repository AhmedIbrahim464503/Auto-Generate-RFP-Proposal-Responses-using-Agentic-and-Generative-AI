from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ProposalSectionResponse(BaseModel):
    id: str
    proposal_plan_id: str
    title: str
    content: Optional[str] = None
    status: str
    owner: Optional[str] = None
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    estimated_hours: int
    dependencies: List[str] = []
    priority: str
    risk_level: str
    is_human_editable: bool

    class Config:
        from_attributes = True

class ComplianceMatrixItemResponse(BaseModel):
    id: str
    compliance_matrix_id: str
    requirement_id: str
    proposal_section_id: Optional[str] = None
    status: str
    explanation: Optional[str] = None
    responsible_department: Optional[str] = None
    responsible_owner: Optional[str] = None
    priority: str
    mandatory: bool
    evidence_required: Optional[str] = None
    source_page: Optional[int] = None
    source_paragraph: Optional[str] = None
    risk_if_missing: Optional[str] = None
    dependencies: List[str] = []
    reviewer: Optional[str] = None
    approval_status: str
    traceability_links: List[str] = []
    confidence: float
    comments: Optional[str] = None

    class Config:
        from_attributes = True

class ProposalTaskResponse(BaseModel):
    id: str
    proposal_plan_id: str
    parent_task_id: Optional[str] = None
    title: str
    owner: Optional[str] = None
    priority: str
    estimated_hours: float
    status: str
    dependencies: List[str] = []
    due_date: Optional[datetime] = None
    is_critical_path: bool

    class Config:
        from_attributes = True

class ProposalMilestoneResponse(BaseModel):
    id: str
    proposal_plan_id: str
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True

class RequiredDocumentResponse(BaseModel):
    id: str
    proposal_plan_id: str
    document_name: str
    document_type: Optional[str] = None
    status: str
    required_by_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class ClarificationRequestResponse(BaseModel):
    id: str
    proposal_plan_id: str
    question: str
    reason: Optional[str] = None
    related_requirement_id: Optional[str] = None
    priority: str
    owner: Optional[str] = None
    status: str
    client_response: Optional[str] = None
    impact: Optional[str] = None
    resolution: Optional[str] = None

    class Config:
        from_attributes = True

class PlanningHistoryResponse(BaseModel):
    id: str
    proposal_plan_id: str
    action: str
    actor: str
    comments: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ProposalPlanResponse(BaseModel):
    id: str
    opportunity_id: str
    title: str
    client: Optional[str] = None
    rfp_name: Optional[str] = None
    proposal_type: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    estimated_duration_days: int
    estimated_effort_hours: int
    complexity: str
    priority: str
    required_departments: List[str] = []
    executive_sponsor: Optional[str] = None
    proposal_owner: Optional[str] = None
    status: str
    version: str
    planning_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    sections: List[ProposalSectionResponse] = []
    tasks: List[ProposalTaskResponse] = []
    milestones: List[ProposalMilestoneResponse] = []
    required_documents: List[RequiredDocumentResponse] = []
    clarification_requests: List[ClarificationRequestResponse] = []
    history: List[PlanningHistoryResponse] = []

    class Config:
        from_attributes = True

class ProposalApproveRequest(BaseModel):
    reviewer: str = Field(..., description="Name of the person signing off on the proposal plan.")
    action: str = Field(..., description="APPROVE or REJECT.")
    comments: Optional[str] = Field(None, description="Approval or rejection notes.")

class ProposalUpdateRequest(BaseModel):
    title: Optional[str] = None
    client: Optional[str] = None
    proposal_owner: Optional[str] = None
    planning_notes: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
