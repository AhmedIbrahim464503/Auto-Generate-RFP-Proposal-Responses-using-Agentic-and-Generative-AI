"""extend reviews and hitl

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
Create Date: 2026-06-26 16:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4d5e6f7a8b9c'
down_revision = '3c4d5e6f7a8b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add columns to financial_review, legal_review, operations_review, technical_review
    tables = ['financial_review', 'legal_review', 'operations_review', 'technical_review']
    for table in tables:
        op.add_column(table, sa.Column('escalation_required', sa.Boolean(), nullable=True, server_default='0'))
        op.add_column(table, sa.Column('is_overridden', sa.Boolean(), nullable=True, server_default='0'))
        op.add_column(table, sa.Column('override_decision', sa.String(50), nullable=True))
        op.add_column(table, sa.Column('override_reason', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('overridden_by', sa.String(100), nullable=True))
        op.add_column(table, sa.Column('override_timestamp', sa.DateTime(), nullable=True))
        op.add_column(table, sa.Column('findings', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('assumptions', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('missing_information', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('clarification_questions', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('reviewer_metadata', sa.Text(), nullable=True))
        op.add_column(table, sa.Column('processing_metadata', sa.Text(), nullable=True))

    # 2. Create review_comment table
    op.create_table(
        'review_comment',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('department', sa.String(50), nullable=False),
        sa.Column('reviewer', sa.String(100), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 3. Create review_override_history table
    op.create_table(
        'review_override_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('department', sa.String(50), nullable=False),
        sa.Column('previous_decision', sa.String(50), nullable=False),
        sa.Column('new_decision', sa.String(50), nullable=False),
        sa.Column('override_reason', sa.Text(), nullable=False),
        sa.Column('overridden_by', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('review_override_history')
    op.drop_table('review_comment')
