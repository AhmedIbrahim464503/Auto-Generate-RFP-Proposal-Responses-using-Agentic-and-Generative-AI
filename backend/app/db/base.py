# Import all models so that Base.metadata has them registered before Alembic runs
from backend.app.db.base_class import Base  # noqa
from backend.app.models.opportunity import Opportunity  # noqa
from backend.app.models.document import (  # noqa
    RFPDocument,
    Requirement,
    Deliverable,
    EvaluationCriteria,
    SubmissionInstruction,
)
from backend.app.models.review import (  # noqa
    FinancialReview,
    LegalReview,
    OperationsReview,
    TechnicalReview,
    ReviewComment,
    ReviewOverrideHistory,
)
from backend.app.models.qualification import (  # noqa
    QualificationDecision,
    QualificationScoringBreakdown,
    QualificationDecisionHistory,
    QualificationExecutiveComment,
    QualificationRule,
)
from backend.app.models.proposal import (  # noqa
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
from backend.app.models.audit import (  # noqa
    AuditEvent,
    ApprovalGate,
    ApprovalDecision,
    AgentExecution,
)
from backend.app.models.system import (  # noqa
    SystemConfiguration,
)
from backend.app.models.knowledge import (  # noqa
    KnowledgeAsset,
    KnowledgeChunk,
    SearchLog,
    GovernanceRecord,
)
from backend.app.models.analysis import (  # noqa
    DocumentSection,
    RFPMetadata,
)
from backend.app.models.proposal_generation import (  # noqa
    GeneratedSection,
    GenerationHistory,
    ProposalCitation,
    ProposalEvidenceLink,
)
from backend.app.models.requirement_intelligence import (  # noqa
    ComplianceObligation,
    RFPRisk,
    RFPAssumption,
    ClarificationQuestion,
    KnowledgeGraphEdge,
    RequirementAssignment,
)
from backend.app.models.ai_platform import (  # noqa
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
from backend.app.models.proposal_review import (  # noqa
    ProposalReviewSession,
    ProposalReviewFinding,
    ProposalReviewScore,
    ProposalReviewWorkflow,
    ProposalReviewAudit,
)
from backend.app.models.workflow import (  # noqa
    WorkflowExecution,
    WorkflowCheckpoint,
    WorkflowEvent,
    WorkflowMetric,
    WorkflowApprovalGate,
)
