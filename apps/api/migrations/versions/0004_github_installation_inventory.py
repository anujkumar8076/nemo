"""Add tenant-owned GitHub installation repository inventory.

Revision ID: 0004_github_install_inventory
Revises: 0003_github_webhook_ingress
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_github_install_inventory"
down_revision: str | None = "0003_github_webhook_ingress"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "github_installations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.BigInteger(), nullable=False),
        sa.Column("account_external_id", sa.BigInteger(), nullable=False),
        sa.Column("account_login", sa.String(length=255), nullable=False),
        sa.Column("account_type", sa.String(length=32), nullable=False),
        sa.Column("repository_selection", sa.String(length=16), nullable=False),
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
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
            "account_type IN ('Organization', 'User')",
            name="ck_github_installations_account_type",
        ),
        sa.CheckConstraint(
            "repository_selection IN ('all', 'selected')",
            name="ck_github_installations_repository_selection",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'suspended', 'revoked')",
            name="ck_github_installations_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", name="uq_github_installations_external_id"),
        sa.UniqueConstraint("organization_id", "id", name="uq_github_installations_org_id"),
    )
    op.create_index(
        "ix_github_installations_org_status",
        "github_installations",
        ["organization_id", "status"],
    )
    op.create_table(
        "github_installation_repositories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("installation_id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.BigInteger(), nullable=False),
        sa.Column("node_id", sa.String(length=255), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("html_url", sa.String(length=2048), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("disabled", sa.Boolean(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["organization_id", "installation_id"],
            ["github_installations.organization_id", "github_installations.id"],
            ondelete="CASCADE",
            name="fk_github_installation_repositories_org_installation",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "installation_id",
            "external_id",
            name="uq_github_installation_repositories_installation_external",
        ),
    )
    op.create_index(
        "ix_github_installation_repositories_org_available",
        "github_installation_repositories",
        ["organization_id", "available"],
    )
    op.create_index(
        "ix_github_installation_repositories_installation",
        "github_installation_repositories",
        ["installation_id", "external_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_github_installation_repositories_installation",
        table_name="github_installation_repositories",
    )
    op.drop_index(
        "ix_github_installation_repositories_org_available",
        table_name="github_installation_repositories",
    )
    op.drop_table("github_installation_repositories")
    op.drop_index("ix_github_installations_org_status", table_name="github_installations")
    op.drop_table("github_installations")
