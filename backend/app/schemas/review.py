from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class DepartmentReviewOutput(BaseModel):
    decision: str = Field(..., description="GO, NO_GO, or CONDITIONALLY_GO")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Explainable details on reasoning")
    evidence: str = Field(..., description="Source quotes/text from RFP")
    findings: List[str] = Field(default_factory=list, description="Specific findings parsed")
    risks: List[str] = Field(default_factory=list, description="Extracted department specific risks")
    assumptions: List[str] = Field(default_factory=list, description="Identified assumptions")
    missing_information: List[str] = Field(default_factory=list, description="Missing items list")
    clarification_questions: List[str] = Field(default_factory=list, description="Questions suggested for client")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    escalation_required: bool = Field(False, description="Whether workflow triggers escalation rules")

class AggregatedRiskResponse(BaseModel):
    id: Optional[str] = None
    severity: str
    likelihood: str
    business_impact: str
    mitigation: str
    mitigation_suggestion: Optional[str] = None
    owning_department: str
    description: str
    confidence: Optional[float] = 1.0

class ReviewCommentRequest(BaseModel):
    comment_text: str
    reviewer: str = "Human Reviewer"

class ReviewOverrideRequest(BaseModel):
    new_decision: str
    override_reason: str
    overridden_by: str = "Capture Manager"

class ReviewApproveRequest(BaseModel):
    reviewer: str = "Human Reviewer"

class DepartmentStatusResponse(BaseModel):
    status: str  # PENDING, REVIEWED, APPROVED, OVERRIDDEN, ESCALATED
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reviewer: Optional[str] = None
    escalation_required: bool = False
    is_overridden: bool = False
    override_decision: Optional[str] = None
    override_reason: Optional[str] = None
    findings: List[str] = []
    risks: List[str] = []
    evidence: Optional[str] = None
    recommendations: List[str] = []

class AllReviewsStatusResponse(BaseModel):
    opportunity_id: str
    financial: DepartmentStatusResponse
    legal: DepartmentStatusResponse
    operations: DepartmentStatusResponse
    technical: DepartmentStatusResponse
