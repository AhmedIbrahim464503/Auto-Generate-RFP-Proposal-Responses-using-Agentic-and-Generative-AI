from typing import List, Optional
from pydantic import BaseModel, Field

class BaseAIOutput(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    evidence: str = Field(..., description="Verbatim text quote from the RFP as source proof")
    reasoning: str = Field(..., description="LLM logic explaining why this item was extracted")
    validation_status: str = Field("VALIDATED", description="Status of validation rules validation")

class RequirementExtractionOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier to build relations e.g. REQ-001")
    title: str = Field(..., description="Short title describing the requirement")
    text_content: str = Field(..., description="Detailed text content of the requirement")
    category: str = Field("Technical", description="e.g. Technical, Legal, Financial, Operational, Security, etc.")
    priority: str = Field("Medium", description="Priority level: High, Medium, Low")
    req_type: str = Field("Functional", description="Type: Functional or Non-Functional")
    mandatory: bool = Field(True, description="Whether the requirement is mandatory or optional")
    source_section: Optional[str] = Field(None, description="Header section where requirement was found")
    source_page: Optional[int] = Field(None, description="Page index where requirement was found")
    temp_parent_id: Optional[str] = Field(None, description="Parent requirement identifier if nested")
    assigned_departments: List[str] = Field(default_factory=list, description="List of responsible departments")

class DeliverableExtractionOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. DEL-001")
    description: str = Field(..., description="Description of the deliverable")
    due_stage: Optional[str] = Field(None, description="Stage/deadline when due")
    mandatory: bool = Field(True, description="Whether this deliverable is mandatory")
    responsible_department: Optional[str] = Field(None, description="Responsible department")
    related_requirements: List[str] = Field(default_factory=list, description="List of related requirement temp IDs")

class EvaluationCriteriaOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. EVA-001")
    criteria_text: str = Field(..., description="Text of the evaluation factor")
    weight: Optional[str] = Field(None, description="Weight percentage or score points")
    factor: Optional[str] = Field(None, description="General category or factor title")
    scoring_methodology: Optional[str] = Field(None, description="How points are scored")
    ranking_criteria: Optional[str] = Field(None, description="How vendors are ranked")
    selection_method: Optional[str] = Field(None, description="Method of final vendor choice")
    tie_break_rules: Optional[str] = Field(None, description="How ties are resolved")
    preferred_experience: Optional[str] = Field(None, description="Experience preferments")
    preferred_certifications: Optional[str] = Field(None, description="Certification preferments")

class SubmissionInstructionOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. SUB-001")
    instruction_text: str = Field(..., description="Core instruction text")
    format_type: Optional[str] = Field(None, description="e.g. PDF, Word, Excel")
    submission_method: Optional[str] = Field(None, description="Portal, Email, Post")
    portal: Optional[str] = Field(None, description="URL or portal name")
    email: Optional[str] = Field(None, description="Submission email address")
    file_naming_rules: Optional[str] = Field(None, description="Formatting naming rules")
    file_formats: Optional[str] = Field(None, description="Accepted file extensions")
    max_size: Optional[str] = Field(None, description="Max size limit")
    required_signatures: Optional[str] = Field(None, description="Signatures required")
    required_forms: Optional[str] = Field(None, description="Forms to fill out")
    num_copies: Optional[int] = Field(None, description="Number of copies")
    submission_sequence: Optional[str] = Field(None, description="Submission sequence/order")
    late_policy: Optional[str] = Field(None, description="Late submission policy")

class ComplianceItemOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. COM-001")
    name: str = Field(..., description="Obligation name, e.g. Insurance, E-Verify")
    status: str = Field("Unknown", description="Status: Unknown, Compliant, Non-Compliant")
    department_owner: Optional[str] = Field(None, description="Assigned department owner")
    evidence_required: Optional[str] = Field(None, description="What constitutes proof of compliance")
    priority: str = Field("Medium", description="Priority level: High, Medium, Low")
    blocking: bool = Field(False, description="Whether missing this blocks proposal submission")

class RiskOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. RSK-001")
    description: str = Field(..., description="Details of the risk identified")
    severity: str = Field("Medium", description="High, Medium, Low")
    likelihood: str = Field("Medium", description="High, Medium, Low")
    business_impact: Optional[str] = Field(None, description="Impact on the proposal or bid")
    mitigation_suggestion: Optional[str] = Field(None, description="Suggested mitigation strategy")
    related_requirements: List[str] = Field(default_factory=list, description="Related requirement temp IDs")

class AssumptionOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. ASM-001")
    description: str = Field(..., description="Details of the assumption")
    category: str = Field("Business", description="Business, Technical, Operational, Contractual")
    is_explicit: bool = Field(True, description="True if explicitly stated, False if inferred")

class ClarificationQuestionOutput(BaseAIOutput):
    temp_id: str = Field(..., description="Temporary identifier e.g. QST-001")
    question_text: str = Field(..., description="Suggested question to ask the client")
    priority: str = Field("Medium", description="High, Medium, Low")
    reason: Optional[str] = Field(None, description="Why this clarification is needed")
    suggested_recipient: Optional[str] = Field(None, description="Target recipient of the question")
    business_impact: Optional[str] = Field(None, description="Impact if left unanswered")
    related_requirements: List[str] = Field(default_factory=list, description="Related requirement temp IDs")

class KnowledgeGraphEdgeOutput(BaseModel):
    source_id: str = Field(..., description="temp_id of source entity")
    source_type: str = Field(..., description="Type of source entity")
    target_id: str = Field(..., description="temp_id of target entity")
    target_type: str = Field(..., description="Type of target entity")
    relationship_type: str = Field(..., description="Type of relationship, e.g. triggers, mitigates, requires")

class RequirementIntelligenceOutput(BaseModel):
    requirements: List[RequirementExtractionOutput] = []
    deliverables: List[DeliverableExtractionOutput] = []
    evaluation_criteria: List[EvaluationCriteriaOutput] = []
    submission_instructions: List[SubmissionInstructionOutput] = []
    compliance_items: List[ComplianceItemOutput] = []
    risks: List[RiskOutput] = []
    assumptions: List[AssumptionOutput] = []
    clarification_questions: List[ClarificationQuestionOutput] = []
    knowledge_graph_edges: List[KnowledgeGraphEdgeOutput] = []
