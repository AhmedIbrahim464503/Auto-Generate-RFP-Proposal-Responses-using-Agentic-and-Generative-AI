"""create proposal planning tables

Revision ID: 6f7a8b9c0d1e
Revises: 5e6f7a8b9c0d
Create Date: 2026-06-26 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6f7a8b9c0d1e'
down_revision = '5e6f7a8b9c0d'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Drop existing basic tables (child first)
    op.drop_table('compliance_item')
    op.drop_table('compliance_matrix')
    op.drop_table('proposal_section')
    op.drop_table('proposal_plan')

    # 2. Create extended proposal_plan
    op.create_table(
        'proposal_plan',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('client', sa.String(255), nullable=True),
        sa.Column('rfp_name', sa.String(255), nullable=True),
        sa.Column('proposal_type', sa.String(100), nullable=True),
        sa.Column('submission_deadline', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration_days', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('estimated_effort_hours', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('complexity', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('priority', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('required_departments', sa.Text(), nullable=True),
        sa.Column('executive_sponsor', sa.String(100), nullable=True),
        sa.Column('proposal_owner', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('version', sa.String(50), nullable=False, server_default='v1.0.0'),
        sa.Column('planning_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 3. Create extended proposal_section
    op.create_table(
        'proposal_section',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('owner', sa.String(100), nullable=True),
        sa.Column('reviewer', sa.String(100), nullable=True),
        sa.Column('approver', sa.String(100), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('risk_level', sa.String(50), nullable=True, server_default='Low'),
        sa.Column('is_human_editable', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 4. Create compliance_matrix
    op.create_table(
        'compliance_matrix',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 5. Create extended compliance_item
    op.create_table(
        'compliance_item',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('compliance_matrix_id', sa.String(36), sa.ForeignKey('compliance_matrix.id'), nullable=False),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('proposal_section_id', sa.String(36), sa.ForeignKey('proposal_section.id'), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='Unknown'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('responsible_department', sa.String(100), nullable=True),
        sa.Column('responsible_owner', sa.String(100), nullable=True),
        sa.Column('priority', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('mandatory', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('evidence_required', sa.Text(), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_paragraph', sa.Text(), nullable=True),
        sa.Column('risk_if_missing', sa.Text(), nullable=True),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('reviewer', sa.String(100), nullable=True),
        sa.Column('approval_status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('traceability_links', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 6. Create proposal_task table
    op.create_table(
        'proposal_task',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('parent_task_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('owner', sa.String(100), nullable=True),
        sa.Column('priority', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('estimated_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='TODO'),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('is_critical_path', sa.Boolean(), nullable=False, server_default='0')
    )

    # 7. Create proposal_milestone table
    op.create_table(
        'proposal_milestone',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING')
    )

    # 8. Create required_document table
    op.create_table(
        'required_document',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('document_name', sa.String(255), nullable=False),
        sa.Column('document_type', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='MISSING'),
        sa.Column('required_by_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True)
    )

    # 9. Create clarification_request table
    op.create_table(
        'clarification_request',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('related_requirement_id', sa.String(36), nullable=True),
        sa.Column('priority', sa.String(50), nullable=True, server_default='Medium'),
        sa.Column('owner', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('client_response', sa.Text(), nullable=True),
        sa.Column('impact', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True)
    )

    # 10. Create planning_history table
    op.create_table(
        'planning_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('planning_history')
    op.drop_table('clarification_request')
    op.drop_table('required_document')
    op.drop_table('proposal_milestone')
    op.drop_table('proposal_task')
    op.drop_table('compliance_item')
    op.drop_table('compliance_matrix')
    op.drop_table('proposal_section')
    op.drop_table('proposal_plan')
    
    # Re-create basic ones
    op.create_table(
        'proposal_plan',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )
    op.create_table(
        'proposal_section',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )
    op.create_table(
        'compliance_matrix',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )
    op.create_table(
        'compliance_item',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('compliance_matrix_id', sa.String(36), sa.ForeignKey('compliance_matrix.id'), nullable=False),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )
