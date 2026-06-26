"""phase11 db updates

Revision ID: 10j1k2l3m4n5
Revises: 9i0j1k2l3m4n
Create Date: 2026-06-26 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '10j1k2l3m4n5'
down_revision = '9i0j1k2l3m4n'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. model_registry additions
    op.add_column('model_registry', sa.Column('latency', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('model_registry', sa.Column('availability', sa.Float(), nullable=True, server_default='1.0'))
    op.add_column('model_registry', sa.Column('cost_metadata', sa.JSON(), nullable=True))

    # 2. agent_registry additions
    op.add_column('agent_registry', sa.Column('owner', sa.String(100), nullable=True))
    op.add_column('agent_registry', sa.Column('health_status', sa.String(50), nullable=True, server_default='healthy'))
    op.add_column('agent_registry', sa.Column('approval_status', sa.String(50), nullable=True, server_default='approved'))
    op.add_column('agent_registry', sa.Column('deprecation_status', sa.Boolean(), nullable=True, server_default='0'))

    # 3. prompt_registry additions
    op.add_column('prompt_registry', sa.Column('created_by', sa.String(100), nullable=True))
    op.add_column('prompt_registry', sa.Column('last_updated', sa.DateTime(), nullable=True))

    # 4. Create governance_policy
    op.create_table(
        'governance_policy',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('rules_payload', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1')
    )

def downgrade() -> None:
    op.drop_table('governance_policy')
    op.drop_column('prompt_registry', 'last_updated')
    op.drop_column('prompt_registry', 'created_by')
    op.drop_column('agent_registry', 'deprecation_status')
    op.drop_column('agent_registry', 'approval_status')
    op.drop_column('agent_registry', 'health_status')
    op.drop_column('agent_registry', 'owner')
    op.drop_column('model_registry', 'cost_metadata')
    op.drop_column('model_registry', 'availability')
    op.drop_column('model_registry', 'latency')
