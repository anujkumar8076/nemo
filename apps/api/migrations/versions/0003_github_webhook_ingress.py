"""Add durable GitHub webhook ingress records.

Revision ID: 0003_github_webhook_ingress
Revises: 0002_platform_skeleton
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_github_webhook_ingress"
down_revision: str | None = "0002_platform_skeleton"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "github_webhook_deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("delivery_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("installation_external_id", sa.BigInteger(), nullable=True),
        sa.Column("repository_external_id", sa.BigInteger(), nullable=True),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'ignored', 'processed', 'failed')",
            name="ck_github_webhook_deliveries_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id", name="uq_github_webhook_deliveries_delivery_id"),
    )
    op.create_index(
        "ix_github_webhook_deliveries_status_received",
        "github_webhook_deliveries",
        ["status", "received_at"],
    )
    op.create_index(
        "ix_github_webhook_deliveries_installation",
        "github_webhook_deliveries",
        ["installation_external_id", "received_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_github_webhook_deliveries_installation",
        table_name="github_webhook_deliveries",
    )
    op.drop_index(
        "ix_github_webhook_deliveries_status_received",
        table_name="github_webhook_deliveries",
    )
    op.drop_table("github_webhook_deliveries")
