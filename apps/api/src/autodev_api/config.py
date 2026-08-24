from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated server configuration loaded from AUTODEV_* variables."""

    model_config = SettingsConfigDict(
        env_prefix="AUTODEV_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = Field(min_length=1)
    redis_url: str = Field(min_length=1)
    temporal_address: str = Field(min_length=1)
    temporal_namespace: str = "default"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
