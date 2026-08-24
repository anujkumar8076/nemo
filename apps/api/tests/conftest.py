import os

os.environ.setdefault(
    "AUTODEV_DATABASE_URL", "postgresql+psycopg://autodev:autodev@localhost:5432/autodev"
)
os.environ.setdefault("AUTODEV_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("AUTODEV_TEMPORAL_ADDRESS", "localhost:7233")
