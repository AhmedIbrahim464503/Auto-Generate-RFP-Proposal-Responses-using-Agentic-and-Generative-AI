"""create qualification tables

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-06-26 17:02:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5e6f7a8b9c0d'
down_revision = '4d5e6f7a8b9c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Drop existing basic qualification_decision table
    op.drop_table('qualification_decision')

    # 2. Create extended qualification_decision table
    op.create_table(
        'qualification_decision',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('recommendation', sa.String(50), nullable=False),
        sa.Column('final_decision', sa.String(50), nullable=True),
        sa.Column('decision_by', sa.String(100), nullable=True),
        sa.Column('decision_timestamp', sa.DateTime(), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('evidence_json', sa.Text(), nullable=True),
        sa.Column('positive_factors', sa.Text(), nullable=True),
        sa.Column('negative_factors', sa.Text(), nullable=True),
        sa.Column('blocking_issues', sa.Text(), nullable=True),
        sa.Column('mitigating_factors', sa.Text(), nullable=True),
        sa.Column('recommended_actions', sa.Text(), nullable=True),
        sa.Column('escalation_requirements', sa.Text(), nullable=True),
        sa.Column('outstanding_clarifications', sa.Text(), nullable=True),
        sa.Column('next_steps', sa.Text(), nullable=True),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('opportunity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('estimated_win_probability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('win_probability_explanation', sa.Text(), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('rule_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
    )

    # 3. Create qualification_scoring_breakdown table
    op.create_table(
        'qualification_scoring_breakdown',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('qualification_id', sa.String(36), sa.ForeignKey('qualification_decision.id'), nullable=False),
        sa.Column('dimension', sa.String(50), nullable=False),
        sa.Column('raw_score', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('weighted_score', sa.Float(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=True)
    )

    # 4. Create qualification_decision_history table
    op.create_table(
        'qualification_decision_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('previous_status', sa.String(50), nullable=True),
        sa.Column('new_status', sa.String(50), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 5. Create qualification_executive_comment table
    op.create_table(
        'qualification_executive_comment',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('qualification_id', sa.String(36), sa.ForeignKey('qualification_decision.id'), nullable=False),
        sa.Column('author', sa.String(100), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False)
    )

    # 6. Create qualification_rule table
    op.create_table(
        'qualification_rule',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('scope_key', sa.String(100), nullable=False, server_default='global'),
        sa.Column('rules_payload', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('qualification_rule')
    op.drop_table('qualification_executive_comment')
    op.drop_table('qualification_decision_history')
    op.drop_table('qualification_scoring_breakdown')
    op.drop_table('qualification_decision')
    # Recreate the old basic qualification_decision table
    op.create_table(
        'qualification_decision',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('opportunity_id', sa.String(36), sa.ForeignKey('opportunity.id'), nullable=False),
        sa.Column('final_decision', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('risks', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
    )
