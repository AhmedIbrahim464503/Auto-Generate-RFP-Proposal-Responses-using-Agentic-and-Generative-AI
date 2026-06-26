"""create requirement intelligence tables

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2026-06-26 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c4d5e6f7a8b'
down_revision = '2b3c4d5e6f7a'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add new columns to existing tables
    # requirement
    op.add_column('requirement', sa.Column('priority', sa.String(50), nullable=True))
    op.add_column('requirement', sa.Column('req_type', sa.String(100), nullable=True))
    op.add_column('requirement', sa.Column('mandatory', sa.Boolean(), nullable=True, server_default='1'))
    op.add_column('requirement', sa.Column('source_section', sa.String(255), nullable=True))
    op.add_column('requirement', sa.Column('source_page', sa.Integer(), nullable=True))
    op.add_column('requirement', sa.Column('parent_id', sa.String(36), nullable=True))
    op.add_column('requirement', sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))

    # deliverable
    op.add_column('deliverable', sa.Column('due_stage', sa.String(100), nullable=True))
    op.add_column('deliverable', sa.Column('mandatory', sa.Boolean(), nullable=True, server_default='1'))
    op.add_column('deliverable', sa.Column('responsible_department', sa.String(100), nullable=True))
    op.add_column('deliverable', sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))

    # evaluation_criteria
    op.add_column('evaluation_criteria', sa.Column('factor', sa.String(255), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('scoring_methodology', sa.Text(), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('ranking_criteria', sa.Text(), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('selection_method', sa.String(100), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('tie_break_rules', sa.Text(), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('preferred_experience', sa.Text(), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('preferred_certifications', sa.Text(), nullable=True))
    op.add_column('evaluation_criteria', sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))

    # submission_instruction
    op.add_column('submission_instruction', sa.Column('submission_method', sa.String(100), nullable=True))
    op.add_column('submission_instruction', sa.Column('portal', sa.String(255), nullable=True))
    op.add_column('submission_instruction', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('submission_instruction', sa.Column('file_naming_rules', sa.String(255), nullable=True))
    op.add_column('submission_instruction', sa.Column('file_formats', sa.String(255), nullable=True))
    op.add_column('submission_instruction', sa.Column('max_size', sa.String(100), nullable=True))
    op.add_column('submission_instruction', sa.Column('required_signatures', sa.Text(), nullable=True))
    op.add_column('submission_instruction', sa.Column('required_forms', sa.Text(), nullable=True))
    op.add_column('submission_instruction', sa.Column('num_copies', sa.Integer(), nullable=True))
    op.add_column('submission_instruction', sa.Column('submission_sequence', sa.Text(), nullable=True))
    op.add_column('submission_instruction', sa.Column('late_policy', sa.Text(), nullable=True))
    op.add_column('submission_instruction', sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))

    # 2. Create new tables
    # compliance_obligation
    op.create_table(
        'compliance_obligation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='Unknown'),
        sa.Column('department_owner', sa.String(100), nullable=True),
        sa.Column('evidence_required', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(50), nullable=True),
        sa.Column('blocking', sa.Boolean(), nullable=False, default=False),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
    )

    # rfp_risk
    op.create_table(
        'rfp_risk',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('requirement_id', sa.String(36), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(50), nullable=True),
        sa.Column('likelihood', sa.String(50), nullable=True),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('mitigation_suggestion', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
    )

    # rfp_assumption
    op.create_table(
        'rfp_assumption',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_explicit', sa.Boolean(), nullable=False, default=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
    )

    # clarification_question
    op.create_table(
        'clarification_question',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('requirement_id', sa.String(36), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(50), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('suggested_recipient', sa.String(100), nullable=True),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
    )

    # knowledge_graph_edge
    op.create_table(
        'knowledge_graph_edge',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('source_id', sa.String(36), nullable=False),
        sa.Column('target_type', sa.String(100), nullable=False),
        sa.Column('target_id', sa.String(36), nullable=False),
        sa.Column('relationship_type', sa.String(100), nullable=False),
    )

    # requirement_assignment
    op.create_table(
        'requirement_assignment',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('requirement_id', sa.String(36), sa.ForeignKey('requirement.id'), nullable=False),
        sa.Column('department_name', sa.String(100), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('requirement_assignment')
    op.drop_table('knowledge_graph_edge')
    op.drop_table('clarification_question')
    op.drop_table('rfp_assumption')
    op.drop_table('rfp_risk')
    op.drop_table('compliance_obligation')
    
    # SQLite does not support dropping columns directly, but since we are focusing on upgrade scripts for portability,
    # we can omit complex downgrades for columns here.
