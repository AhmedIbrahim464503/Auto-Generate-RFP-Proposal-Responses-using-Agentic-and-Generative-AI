from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument, Requirement, Deliverable, EvaluationCriteria, SubmissionInstruction
from backend.app.models.review import (
    FinancialReview,
    LegalReview,
    OperationsReview,
    TechnicalReview,
    ReviewComment,
    ReviewOverrideHistory,
)
from backend.app.models.qualification import (
    QualificationDecision,
    QualificationScoringBreakdown,
    QualificationDecisionHistory,
    QualificationExecutiveComment,
    QualificationRule,
)
from backend.app.models.proposal import (
    ProposalPlan,
    ComplianceMatrix,
    ComplianceItem,
    ProposalSection,
    ProposalTask,
    ProposalMilestone,
    RequiredDocument,
    ClarificationRequest,
    PlanningHistory,
)
from backend.app.models.audit import AuditEvent, ApprovalGate, ApprovalDecision, AgentExecution
from backend.app.models.system import SystemConfiguration
from backend.app.models.knowledge import KnowledgeAsset, KnowledgeChunk, SearchLog, GovernanceRecord
from backend.app.models.analysis import DocumentSection, RFPMetadata
from backend.app.models.proposal_generation import GeneratedSection, GenerationHistory, ProposalCitation, ProposalEvidenceLink
from backend.app.models.requirement_intelligence import (
    ComplianceObligation,
    RFPRisk,
    RFPAssumption,
    ClarificationQuestion,
    KnowledgeGraphEdge,
    RequirementAssignment,
)
from backend.app.models.ai_platform import (
    ModelRegistry,
    AgentRegistry,
    PromptRegistry,
    ToolRegistry,
    WorkflowRegistry,
    CapabilityRegistry,
    AgentMemory,
    AgentMetric,
    ExplainabilityRecord,
    AIConfig,
    GovernancePolicy,
)
from backend.app.models.proposal_review import (
    ProposalReviewSession,
    ProposalReviewFinding,
    ProposalReviewScore,
    ProposalReviewWorkflow,
    ProposalReviewAudit,
)

