"""create domain tables

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-06-25 23:59:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Opportunity
    op.create_table(
        'opportunity',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 2. RFPDocument
    op.create_table(
        'rfp_document',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 3. Requirement
    op.create_table(
        'requirement',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 4. Deliverable
    op.create_table(
        'deliverable',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('deadline', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 5. EvaluationCriteria
    op.create_table(
        'evaluation_criteria',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('criteria_text', sa.Text(), nullable=False),
        sa.Column('weight', sa.String(50), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 6. SubmissionInstruction
    op.create_table(
        'submission_instruction',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('instruction_text', sa.Text(), nullable=False),
        sa.Column('format_type', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 7-10. Reviews
    for dept in ['financial', 'legal', 'operations', 'technical']:
        op.create_table(
            f'{dept}_review',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
            sa.Column('reviewer', sa.String(100), nullable=True),
            sa.Column('decision', sa.String(50), nullable=False),
            sa.Column('confidence', sa.Float(), nullable=False),
            sa.Column('reasoning', sa.Text(), nullable=True),
            sa.Column('evidence', sa.Text(), nullable=True),
            sa.Column('risks', sa.Text(), nullable=True),
            sa.Column('recommendations', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        )

    # 11. QualificationDecision
    op.create_table(
        'qualification_decision',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('final_decision', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('risks', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 12. ProposalPlan
    op.create_table(
        'proposal_plan',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 13. ComplianceMatrix
    op.create_table(
        'compliance_matrix',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 14. ComplianceItem
    op.create_table(
        'compliance_item',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('compliance_matrix_id', sa.String(36), sa.ForeignKey('compliance_matrix.id'), nullable=False),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 15. ProposalSection
    op.create_table(
        'proposal_section',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 16. AuditEvent
    op.create_table(
        'audit_event',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('entity_name', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True),
    )

    # 17. ApprovalGate
    op.create_table(
        'approval_gate',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('gate_number', sa.Integer(), nullable=False),
        sa.Column('gate_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 18. ApprovalDecision
    op.create_table(
        'approval_decision',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('approval_gate_id', sa.String(36), sa.ForeignKey('approval_gate.id'), nullable=False),
        sa.Column('reviewer', sa.String(100), nullable=False),
        sa.Column('decision', sa.String(50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )

    # 19. AgentExecution
    op.create_table(
        'agent_execution',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('decision', sa.String(255), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('risks', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )

    # 20. KnowledgeAsset
    op.create_table(
        'knowledge_asset',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('asset_type', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )

    # 21. SearchResult
    op.create_table(
        'search_result',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('asset_id', sa.String(36), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('retrieved_content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )

    # 22. SystemConfiguration
    op.create_table(
        'system_configuration',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('config_key', sa.String(100), unique=True, nullable=False),
        sa.Column('config_value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    tables = [
        'system_configuration', 'search_result', 'knowledge_asset', 'agent_execution',
        'approval_decision', 'approval_gate', 'audit_event', 'proposal_section',
        'compliance_item', 'compliance_matrix', 'proposal_plan', 'qualification_decision',
        'technical_review', 'operations_review', 'legal_review', 'financial_review',
        'submission_instruction', 'evaluation_criteria', 'deliverable', 'requirement',
        'rfp_document', 'opportunity'
    ]
    for table in tables:
        op.drop_table(table)
