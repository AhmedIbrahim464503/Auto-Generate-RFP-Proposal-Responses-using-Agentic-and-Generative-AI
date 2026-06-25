from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# --- Upload Contracts ---
class UploadResponse(BaseModel):
    success: bool
    rfp_document_id: str
    file_name: str
    uploaded_at: datetime

# --- Requirement Review Contracts ---
class RequirementDetail(BaseModel):
    id: str
    title: str
    text_content: str
    category: str

class RequirementReviewResponse(BaseModel):
    opportunity_id: str
    requirements: List[RequirementDetail]

# --- Department Review Contracts ---
class DepartmentReviewRequest(BaseModel):
    decision: str  # GO, NO_GO, CONDITIONALLY_GO
    confidence: float
    reasoning: str
    evidence: Optional[str] = None
    risks: Optional[str] = None
    recommendations: Optional[str] = None

class DepartmentReviewResponse(BaseModel):
    success: bool
    review_id: str
    opportunity_id: str
    department: str
    decision: str

# --- Qualification Contracts ---
class QualificationRequest(BaseModel):
    final_decision: str  # GO, NO_GO
    reasoning: str
    evidence: Optional[str] = None
    risks: Optional[str] = None

class QualificationResponse(BaseModel):
    opportunity_id: str
    final_decision: str
    confidence: float
    reasoning: str

# --- Planning Contracts ---
class CreatePlanRequest(BaseModel):
    title: str
    section_titles: List[str]

class SectionDetail(BaseModel):
    id: str
    title: str
    status: str

class PlanResponse(BaseModel):
    plan_id: str
    opportunity_id: str
    title: str
    sections: List[SectionDetail]

# --- Proposal Generation Contracts ---
class GenerateProposalRequest(BaseModel):
    proposal_plan_id: str

class GeneratedSection(BaseModel):
    section_id: str
    title: str
    content: str

class ProposalGenerationResponse(BaseModel):
    success: bool
    sections: List[GeneratedSection]

# --- Compliance Review Contracts ---
class ComplianceItemDetail(BaseModel):
    id: str
    requirement_id: str
    status: str  # COMPLIANT, NON_COMPLIANT, PARTIALLY_COMPLIANT
    explanation: str

class ComplianceMatrixResponse(BaseModel):
    compliance_matrix_id: str
    opportunity_id: str
    items: List[ComplianceItemDetail]

# --- Approval Gate Contracts ---
class GateApprovalRequest(BaseModel):
    decision: str  # APPROVED, REJECTED
    comments: Optional[str] = None

class GateApprovalResponse(BaseModel):
    success: bool
    gate_id: str
    gate_number: int
    status: str  # APPROVED, REJECTED, PENDING
    reviewer: str
    timestamp: datetime

# --- Audit & Dashboard Contracts ---
class AuditLogResponse(BaseModel):
    id: str
    actor: str
    action: str
    timestamp: datetime
    entity_name: str
    entity_id: str
    correlation_id: Optional[str] = None

class DashboardSummaryResponse(BaseModel):
    active_opportunities_count: int
    pending_approvals_count: int
    average_compliance_rate: float
    completed_proposals_count: int
