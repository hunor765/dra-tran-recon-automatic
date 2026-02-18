"""Add webhooks and webhook_deliveries tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-17 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('secret', sa.String(), nullable=True),
        sa.Column('events', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=True),
        sa.Column('last_success', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhooks_id'), 'webhooks', ['id'], unique=False)

    # Create webhook_deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.String(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_deliveries_id'), 'webhook_deliveries', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_webhook_deliveries_id'), table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    op.drop_index(op.f('ix_webhooks_id'), table_name='webhooks')
    op.drop_table('webhooks')
