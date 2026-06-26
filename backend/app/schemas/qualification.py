from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class QualificationExplanationOutput(BaseModel):
    executive_summary: str = Field(..., description="High-level executive summary of the evaluation.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the evaluation recommendation.")
    reasoning: str = Field(..., description="Logical step-by-step reasoning behind the recommendations.")
    evidence: List[str] = Field(default_factory=list, description="Citations and evidence lines from the RFP document.")
    positive_factors: List[str] = Field(default_factory=list, description="Factors supporting a positive decision.")
    negative_factors: List[str] = Field(default_factory=list, description="Factors supporting a negative or caution decision.")
    blocking_issues: List[str] = Field(default_factory=list, description="Vetoes or strict blocking clauses identified.")
    mitigating_factors: List[str] = Field(default_factory=list, description="Proposed mitigations for identified risks.")
    recommended_actions: List[str] = Field(default_factory=list, description="Immediate recommended capture actions.")
    escalation_requirements: List[str] = Field(default_factory=list, description="Escalation checkpoints needed for executive approval.")
    outstanding_clarifications: List[str] = Field(default_factory=list, description="Clarifications requested from the client.")
    next_steps: List[str] = Field(default_factory=list, description="Next milestones in the proposal process.")
    business_impact: str = Field(..., description="Estimated long-term business and resource impact.")
    estimated_win_probability: float = Field(..., ge=0.0, le=100.0, description="Estimated win probability percentage (0-100).")
    win_probability_explanation: str = Field(..., description="Reasoning and explanation for the estimated win probability.")

class QualificationScoringBreakdownResponse(BaseModel):
    dimension: str
    raw_score: float
    weight: float
    weighted_score: float
    details: Optional[Dict[str, Any]] = None

class ExecutiveCommentResponse(BaseModel):
    id: str
    author: str
    comment_text: str
    timestamp: datetime

    class Config:
        from_attributes = True

class QualificationDecisionResponse(BaseModel):
    id: str
    opportunity_id: str
    status: str
    recommendation: str
    final_decision: Optional[str] = None
    decision_by: Optional[str] = None
    decision_timestamp: Optional[datetime] = None
    executive_summary: Optional[str] = None
    confidence: float
    reasoning: Optional[str] = None
    evidence: List[str] = []
    positive_factors: List[str] = []
    negative_factors: List[str] = []
    blocking_issues: List[str] = []
    mitigating_factors: List[str] = []
    recommended_actions: List[str] = []
    escalation_requirements: List[str] = []
    outstanding_clarifications: List[str] = []
    next_steps: List[str] = []
    business_impact: Optional[str] = None
    
    opportunity_score: float
    estimated_win_probability: float
    win_probability_explanation: Optional[str] = None
    
    prompt_version: Optional[str] = None
    model_version: Optional[str] = None
    rule_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    scoring_breakdowns: List[QualificationScoringBreakdownResponse] = []
    comments: List[ExecutiveCommentResponse] = []

    class Config:
        from_attributes = True

class QualificationApproveRequest(BaseModel):
    reviewer: str = Field(..., description="Name of the executive approving the decision.")
    comments: Optional[str] = Field(None, description="Optional comments during sign-off.")

class QualificationOverrideRequest(BaseModel):
    new_decision: str = Field(..., description="GO, GO_WITH_CONDITIONS, ESCALATE, or NO_GO.")
    override_reason: str = Field(..., description="Explanation of why the recommendation is overridden.")
    overridden_by: str = Field(..., description="Name of the authorized manager performing the override.")
    comments: Optional[str] = Field(None, description="Optional comments during override.")

class QualificationRecalculateRequest(BaseModel):
    weights: Dict[str, float] = Field(..., description="Map of dimensions to custom float weights.")

class QualificationRuleResponse(BaseModel):
    id: str
    version: str
    name: str
    scope_key: str
    rules_payload: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class QualificationRuleUpdateRequest(BaseModel):
    rules_payload: Dict[str, Any] = Field(..., description="Complete new configuration schema payload.")

class ExecutiveCommentCreateRequest(BaseModel):
    author: str = Field(..., description="Comment author's name.")
    comment_text: str = Field(..., description="Comment narrative.")

class DecisionHistoryResponse(BaseModel):
    id: str
    opportunity_id: str
    action: str
    actor: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    comments: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
