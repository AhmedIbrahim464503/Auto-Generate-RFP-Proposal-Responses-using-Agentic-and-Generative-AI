"""phase12 db reviews

Revision ID: 11k2l3m4n5o6
Revises: 10j1k2l3m4n5
Create Date: 2026-06-27 00:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '11k2l3m4n5o6'
down_revision = '10j1k2l3m4n5'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create proposal_review_session
    op.create_table(
        'proposal_review_session',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='AWAIT_HUMAN_REVIEW'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('meta_payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 2. Create proposal_review_finding
    op.create_table(
        'proposal_review_finding',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('proposal_review_session.id', ondelete='CASCADE'), nullable=False),
        sa.Column('generated_section_id', sa.String(36), sa.ForeignKey('generated_section.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='warning'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 3. Create proposal_review_score
    op.create_table(
        'proposal_review_score',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('proposal_review_session.id', ondelete='CASCADE'), nullable=False),
        sa.Column('generated_section_id', sa.String(36), sa.ForeignKey('generated_section.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_name', sa.String(50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 4. Create proposal_review_workflow
    op.create_table(
        'proposal_review_workflow',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('stages', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 5. Create proposal_review_audit
    op.create_table(
        'proposal_review_audit',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('proposal_review_session.id', ondelete='CASCADE'), nullable=False),
        sa.Column('generated_section_id', sa.String(36), sa.ForeignKey('generated_section.id', ondelete='CASCADE'), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('proposal_review_audit')
    op.drop_table('proposal_review_workflow')
    op.drop_table('proposal_review_score')
    op.drop_table('proposal_review_finding')
    op.drop_table('proposal_review_session')
