from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ProposalReviewFindingBase(BaseModel):
    generated_section_id: str
    agent_id: str
    category: str
    severity: str
    message: str
    evidence: Optional[str] = None

class ProposalReviewFindingCreate(ProposalReviewFindingBase):
    pass

class ProposalReviewFindingResponse(ProposalReviewFindingBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProposalReviewScoreBase(BaseModel):
    generated_section_id: str
    metric_name: str
    score: float
    weight: float

class ProposalReviewScoreCreate(ProposalReviewScoreBase):
    pass

class ProposalReviewScoreResponse(ProposalReviewScoreBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProposalReviewAuditBase(BaseModel):
    generated_section_id: Optional[str] = None
    action: str
    actor: str
    payload: Optional[Dict[str, Any]] = None

class ProposalReviewAuditCreate(ProposalReviewAuditBase):
    pass

class ProposalReviewAuditResponse(ProposalReviewAuditBase):
    id: str
    session_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ProposalReviewSessionBase(BaseModel):
    proposal_plan_id: str
    status: str
    overall_score: float
    meta_payload: Optional[Dict[str, Any]] = None

class ProposalReviewSessionResponse(ProposalReviewSessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    findings: List[ProposalReviewFindingResponse] = []
    scores: List[ProposalReviewScoreResponse] = []
    audits: List[ProposalReviewAuditResponse] = []

    class Config:
        from_attributes = True


class ProposalReviewWorkflowBase(BaseModel):
    name: str
    stages: List[str]
    is_active: Optional[bool] = True

class ProposalReviewWorkflowCreate(ProposalReviewWorkflowBase):
    pass

class ProposalReviewWorkflowResponse(ProposalReviewWorkflowBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class StartReviewRequest(BaseModel):
    proposal_plan_id: str
    workflow_id: Optional[str] = None

class RefineReviewRequest(BaseModel):
    session_id: str

class HumanDecisionRequest(BaseModel):
    session_id: str
    actor: str
    message: Optional[str] = None
    override_payload: Optional[Dict[str, Any]] = None
