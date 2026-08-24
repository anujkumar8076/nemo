"""Add one-time tenant-bound GitHub installation claim sessions.

Revision ID: 0005_github_install_claims
Revises: 0004_github_install_inventory
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_github_install_claims"
down_revision: str | None = "0004_github_install_inventory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "github_installation_claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("initiated_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("state_digest", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("installation_external_id", sa.BigInteger(), nullable=True),
        sa.Column("verified_github_user_external_id", sa.BigInteger(), nullable=True),
        sa.Column("verified_github_user_login", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('awaiting_setup', 'awaiting_authorization', 'completed')",
            name="ck_github_installation_claims_status",
        ),
        sa.CheckConstraint(
            "(status = 'awaiting_setup' AND installation_external_id IS NULL "
            "AND consumed_at IS NULL AND verified_github_user_external_id IS NULL "
            "AND verified_github_user_login IS NULL) OR "
            "(status = 'awaiting_authorization' AND installation_external_id IS NOT NULL "
            "AND consumed_at IS NULL AND verified_github_user_external_id IS NULL "
            "AND verified_github_user_login IS NULL) OR "
            "(status = 'completed' AND installation_external_id IS NOT NULL "
            "AND consumed_at IS NOT NULL AND verified_github_user_external_id IS NOT NULL "
            "AND verified_github_user_login IS NOT NULL)",
            name="ck_github_installation_claims_stage_fields",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["initiated_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_digest", name="uq_github_installation_claims_state_digest"),
    )
    op.create_index(
        "ix_github_installation_claims_org_created",
        "github_installation_claims",
        ["organization_id", "created_at"],
    )
    op.create_index(
        "ix_github_installation_claims_expiry",
        "github_installation_claims",
        ["expires_at", "consumed_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_github_installation_claims_expiry",
        table_name="github_installation_claims",
    )
    op.drop_index(
        "ix_github_installation_claims_org_created",
        table_name="github_installation_claims",
    )
    op.drop_table("github_installation_claims")
