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
    QualificationDecision,
)
from backend.app.models.proposal import (  # noqa
    ProposalPlan,
    ComplianceMatrix,
    ComplianceItem,
    ProposalSection,
)
from backend.app.models.audit import (  # noqa
    AuditEvent,
    ApprovalGate,
    ApprovalDecision,
    AgentExecution,
)
from backend.app.models.system import (  # noqa
    KnowledgeAsset,
    SearchResult,
    SystemConfiguration,
)
