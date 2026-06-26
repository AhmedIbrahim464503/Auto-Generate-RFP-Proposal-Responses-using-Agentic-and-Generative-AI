"""create ai platform tables

Revision ID: 9i0j1k2l3m4n
Revises: 8h9i0j1k2l3m
Create Date: 2026-06-26 23:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9i0j1k2l3m4n'
down_revision = '8h9i0j1k2l3m'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create model_registry
    op.create_table(
        'model_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('api_endpoint', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 2. Create agent_registry
    op.create_table(
        'agent_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('capabilities', sa.JSON(), nullable=False),
        sa.Column('supported_tools', sa.JSON(), nullable=False),
        sa.Column('supported_models', sa.JSON(), nullable=False),
        sa.Column('prompt_versions', sa.JSON(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False)
    )

    # 3. Create prompt_registry
    op.create_table(
        'prompt_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_id', sa.String(36), nullable=True),
        sa.Column('prompt_name', sa.String(100), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('developer_prompt', sa.Text(), nullable=True),
        sa.Column('user_template', sa.Text(), nullable=True),
        sa.Column('output_schema', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('rollback_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 4. Create tool_registry
    op.create_table(
        'tool_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('tool_type', sa.String(100), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False)
    )

    # 5. Create workflow_registry
    op.create_table(
        'workflow_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('definition', sa.JSON(), nullable=False)
    )

    # 6. Create capability_registry
    op.create_table(
        'capability_registry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('agent_id', sa.String(36), nullable=False)
    )

    # 7. Create agent_memory
    op.create_table(
        'agent_memory',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 8. Create agent_metric
    op.create_table(
        'agent_metric',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_id', sa.String(36), nullable=False),
        sa.Column('execution_id', sa.String(36), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='success'),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('human_override', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 9. Create explainability_record
    op.create_table(
        'explainability_record',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=True),
        sa.Column('inputs', sa.JSON(), nullable=False),
        sa.Column('retrieved_evidence', sa.JSON(), nullable=False),
        sa.Column('rules_used', sa.JSON(), nullable=False),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('output_schema', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 10. Create ai_config
    op.create_table(
        'ai_config',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('ai_config')
    op.drop_table('explainability_record')
    op.drop_table('agent_metric')
    op.drop_table('agent_memory')
    op.drop_table('capability_registry')
    op.drop_table('workflow_registry')
    op.drop_table('tool_registry')
    op.drop_table('prompt_registry')
    op.drop_table('agent_registry')
    op.drop_table('model_registry')
