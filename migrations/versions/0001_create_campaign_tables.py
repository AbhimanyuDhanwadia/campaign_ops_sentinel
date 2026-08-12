"""create campaign tables

Revision ID: 0001
Revises:
Create Date: 2026-08-12 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaign_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("brand", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("recommendation", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_campaign_runs_brand", "campaign_runs", ["brand"])
    op.create_index("ix_campaign_runs_status", "campaign_runs", ["status"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recommendation_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("actor", sa.String(length=80), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_audit_events_recommendation_id", "audit_events", ["recommendation_id"])
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_request_id", "audit_events", ["request_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("campaign_runs")
