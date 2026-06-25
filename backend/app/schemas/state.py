from typing import List, Optional
from pydantic import BaseModel, Field

class GraphStateRequirement(BaseModel):
    id: str
    title: str
    text_content: str
    category: str

class GraphStateReview(BaseModel):
    reviewer_type: str  # financial, legal, operations, technical
    decision: str       # GO, NO_GO, CONDITIONALLY_GO
    confidence: float
    reasoning: str
    evidence: List[str]
    risks: List[str]

class GraphStateApproval(BaseModel):
    gate_number: int
    reviewer: str
    decision: str
    comments: Optional[str] = None
    timestamp: str

class GraphStateComplianceItem(BaseModel):
    requirement_id: str
    status: str  # COMPLIANT, NON_COMPLIANT, PARTIALLY_COMPLIANT
    explanation: str

class GraphStateProposalSection(BaseModel):
    title: str
    content: Optional[str] = None
    status: str

class GraphStateAuditMetadata(BaseModel):
    correlation_id: str
    user_actor: str
    created_at: str

class GraphState(BaseModel):
    opportunity_id: str
    opportunity_title: str
    requirements: List[GraphStateRequirement] = Field(default_factory=list)
    reviews: List[GraphStateReview] = Field(default_factory=list)
    qualification_decision: Optional[str] = None  # GO, NO_GO
    qualification_confidence: float = 0.0
    planning_sections: List[GraphStateProposalSection] = Field(default_factory=list)
    compliance_items: List[GraphStateComplianceItem] = Field(default_factory=list)
    approvals: List[GraphStateApproval] = Field(default_factory=list)
    audit: GraphStateAuditMetadata
    current_step: str = "init"
