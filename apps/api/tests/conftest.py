import os

os.environ.setdefault(
    "AUTODEV_DATABASE_URL", "postgresql+psycopg://autodev:autodev@localhost:5432/autodev"
)
os.environ.setdefault("AUTODEV_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("AUTODEV_TEMPORAL_ADDRESS", "localhost:7233")
os.environ.setdefault(
    "AUTODEV_BOOTSTRAP_API_TOKEN",
    "local-development-token-change-before-use-000000000000",
)
os.environ.setdefault("AUTODEV_BOOTSTRAP_USER_ID", "00000000-0000-4000-8000-000000000001")
os.environ.setdefault("AUTODEV_BOOTSTRAP_USER_EMAIL", "developer@example.invalid")
os.environ.setdefault("AUTODEV_BOOTSTRAP_USER_NAME", "Local Developer")
os.environ.setdefault("AUTODEV_BOOTSTRAP_ORGANIZATION_ID", "00000000-0000-4000-8000-000000000002")
os.environ.setdefault("AUTODEV_BOOTSTRAP_ORGANIZATION_NAME", "Local Workspace")
os.environ.setdefault("AUTODEV_BOOTSTRAP_ORGANIZATION_SLUG", "local-workspace")
