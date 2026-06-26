"""create proposal generation tables

Revision ID: 8h9i0j1k2l3m
Revises: 7g8h9i0j1k2l
Create Date: 2026-06-26 23:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8h9i0j1k2l3m'
down_revision = '7g8h9i0j1k2l'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create generated_section
    op.create_table(
        'generated_section',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('proposal_section_id', sa.String(36), sa.ForeignKey('proposal_section.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tone_style', sa.String(50), nullable=False, server_default='Professional'),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('prompt_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('model_version', sa.String(50), nullable=False, server_default='gemini-2.5-flash'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 2. Create generation_history
    op.create_table(
        'generation_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('proposal_plan_id', sa.String(36), sa.ForeignKey('proposal_plan.id'), nullable=False),
        sa.Column('proposal_section_id', sa.String(36), sa.ForeignKey('proposal_section.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('content_snapshot', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 3. Create proposal_citation
    op.create_table(
        'proposal_citation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('generated_section_id', sa.String(36), sa.ForeignKey('generated_section.id', ondelete='CASCADE'), nullable=False),
        sa.Column('paragraph_index', sa.Integer(), nullable=False),
        sa.Column('knowledge_asset_id', sa.String(36), nullable=True),
        sa.Column('knowledge_chunk_id', sa.String(36), nullable=True),
        sa.Column('requirement_id', sa.String(36), nullable=True),
        sa.Column('compliance_item_id', sa.String(36), nullable=True),
        sa.Column('source_title', sa.String(255), nullable=False),
        sa.Column('source_location', sa.String(255), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0')
    )

    # 4. Create proposal_evidence_link
    op.create_table(
        'proposal_evidence_link',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('generated_section_id', sa.String(36), sa.ForeignKey('generated_section.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('source_id', sa.String(36), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='1.0')
    )

def downgrade() -> None:
    op.drop_table('proposal_evidence_link')
    op.drop_table('proposal_citation')
    op.drop_table('generation_history')
    op.drop_table('generated_section')
