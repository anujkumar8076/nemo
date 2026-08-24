from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTODEV_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    temporal_address: str = Field(min_length=1)
    temporal_namespace: str = "default"
    temporal_task_queue: str = "autodev-foundation"


@lru_cache
def get_settings() -> WorkerSettings:
    return WorkerSettings()  # type: ignore[call-arg]
