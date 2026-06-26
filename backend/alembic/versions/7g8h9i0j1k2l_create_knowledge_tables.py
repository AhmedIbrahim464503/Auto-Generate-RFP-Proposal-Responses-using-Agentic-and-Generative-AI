"""create knowledge tables

Revision ID: 7g8h9i0j1k2l
Revises: 6f7a8b9c0d1e
Create Date: 2026-06-26 23:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7g8h9i0j1k2l'
down_revision = '6f7a8b9c0d1e'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Drop existing placeholder tables (search_result first, then knowledge_asset)
    op.drop_table('search_result')
    op.drop_table('knowledge_asset')

    # 2. Create extended knowledge_asset table
    op.create_table(
        'knowledge_asset',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('asset_type', sa.String(100), nullable=True),
        sa.Column('version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('owner', sa.String(100), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('source', sa.String(255), nullable=False, server_default='Upload'),
        sa.Column('approval_status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('expiration_date', sa.DateTime(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_retrieved_at', sa.DateTime(), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('embedding_version', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 3. Create knowledge_chunk table
    op.create_table(
        'knowledge_chunk',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('parent_asset_id', sa.String(36), sa.ForeignKey('knowledge_asset.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_section', sa.String(255), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('source_location', sa.String(255), nullable=True),
        sa.Column('embedding_vector', sa.Text(), nullable=True)
    )

    # 4. Create search_log table
    op.create_table(
        'search_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('filters_json', sa.Text(), nullable=True),
        sa.Column('results_json', sa.Text(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 5. Create governance_record table
    op.create_table(
        'governance_record',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('asset_id', sa.String(36), sa.ForeignKey('knowledge_asset.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('governance_record')
    op.drop_table('search_log')
    op.drop_table('knowledge_chunk')
    op.drop_table('knowledge_asset')

    # Re-create basic ones
    op.create_table(
        'knowledge_asset',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('asset_type', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    op.create_table(
        'search_result',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('asset_id', sa.String(36), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('retrieved_content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )
