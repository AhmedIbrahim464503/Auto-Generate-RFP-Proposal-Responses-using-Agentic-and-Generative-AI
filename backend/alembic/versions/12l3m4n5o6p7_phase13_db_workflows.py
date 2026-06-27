"""phase13 db workflows

Revision ID: 12l3m4n5o6p7
Revises: 11k2l3m4n5o6
Create Date: 2026-06-27 11:51:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '12l3m4n5o6p7'
down_revision = '11k2l3m4n5o6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create workflow_execution
    op.create_table(
        'workflow_execution',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_name', sa.String(100), nullable=False),
        sa.Column('proposal_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='running'),
        sa.Column('current_node', sa.String(100), nullable=False, server_default='init'),
        sa.Column('state', sa.JSON(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 2. Create workflow_checkpoint
    op.create_table(
        'workflow_checkpoint',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('node_name', sa.String(100), nullable=False),
        sa.Column('state', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 3. Create workflow_event
    op.create_table(
        'workflow_event',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 4. Create workflow_metric
    op.create_table(
        'workflow_metric',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('node_name', sa.String(100), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 5. Create workflow_approval_gate
    op.create_table(
        'workflow_approval_gate',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('node_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('requested_at', sa.DateTime(), nullable=False),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.Column('decision_payload', sa.JSON(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('workflow_approval_gate')
    op.drop_table('workflow_metric')
    op.drop_table('workflow_event')
    op.drop_table('workflow_checkpoint')
    op.drop_table('workflow_execution')
