from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator
from datetime import datetime

class DepartmentReviewOutput(BaseModel):
    decision: str = Field("GO", description="GO, NO_GO, or CONDITIONALLY_GO")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    reasoning: str = Field("Review completed.", description="Explainable details on reasoning")
    evidence: Any = Field("", description="Source quotes/text from RFP")
    findings: List[Any] = Field(default_factory=list, description="Specific findings parsed")
    risks: List[Any] = Field(default_factory=list, description="Extracted department specific risks")
    assumptions: List[Any] = Field(default_factory=list, description="Identified assumptions")
    missing_information: List[Any] = Field(default_factory=list, description="Missing items list")
    clarification_questions: List[Any] = Field(default_factory=list, description="Questions suggested for client")
    recommendations: List[Any] = Field(default_factory=list, description="Actionable recommendations")
    escalation_required: bool = Field(False, description="Whether workflow triggers escalation rules")

    @model_validator(mode='before')
    @classmethod
    def normalize_lists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            list_fields = ["findings", "risks", "assumptions", "missing_information", "clarification_questions", "recommendations"]
            for field in list_fields:
                val = data.get(field)
                if val is None:
                    data[field] = []
                elif isinstance(val, str):
                    data[field] = [val]
                elif isinstance(val, dict):
                    data[field] = [f"{k}: {v}" for k, v in val.items()]
                elif not isinstance(val, list):
                    data[field] = [str(val)]
        return data

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
