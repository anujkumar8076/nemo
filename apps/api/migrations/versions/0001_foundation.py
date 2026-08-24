"""Establish the migration baseline."""

revision: str = "0001_foundation"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """No product tables are introduced during the foundation phase."""


def downgrade() -> None:
    """The foundation revision is intentionally reversible and empty."""
