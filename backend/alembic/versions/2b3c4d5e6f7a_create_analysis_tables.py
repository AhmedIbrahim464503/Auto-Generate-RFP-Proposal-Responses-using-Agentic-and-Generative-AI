"""create analysis tables

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-06-26 11:43:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7a'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. DocumentSection
    op.create_table(
        'document_section',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('parent_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('classification', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('page_start', sa.Integer(), nullable=False, default=1),
        sa.Column('page_end', sa.Integer(), nullable=False, default=1),
        sa.Column('hierarchy_level', sa.Integer(), nullable=False, default=1),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
    )

    # 2. RFPMetadata
    op.create_table(
        'rfp_metadata',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rfp_document_id', sa.String(36), sa.ForeignKey('rfp_document.id'), nullable=False),
        sa.Column('document_title', sa.String(255), nullable=True),
        sa.Column('client_name', sa.String(255), nullable=True),
        sa.Column('project_name', sa.String(255), nullable=True),
        sa.Column('rfp_number', sa.String(100), nullable=True),
        sa.Column('issue_date', sa.String(100), nullable=True),
        sa.Column('submission_deadline', sa.String(100), nullable=True),
        sa.Column('contact_info', sa.Text(), nullable=True),
        sa.Column('normalized_submission_deadline', sa.DateTime(), nullable=True),
        sa.Column('normalized_question_deadline', sa.DateTime(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=False, default=1.0),
        sa.Column('quality_report', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=False, default="gemini-2.5-flash"),
        sa.Column('prompt_version', sa.String(50), nullable=False, default="1.0"),
        sa.Column('input_tokens', sa.Integer(), nullable=False, default=0),
        sa.Column('output_tokens', sa.Integer(), nullable=False, default=0),
        sa.Column('inference_time_ms', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('rfp_metadata')
    op.drop_table('document_section')
