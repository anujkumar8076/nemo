from functools import lru_cache
from typing import Literal
from uuid import UUID

from pydantic import Field, SecretStr, model_validator
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
    auth_mode: Literal["bootstrap"] = "bootstrap"
    bootstrap_api_token: SecretStr = Field(min_length=32)
    bootstrap_user_id: UUID
    bootstrap_user_email: str = Field(min_length=3, max_length=320, pattern=r"^[^@]+@[^@]+$")
    bootstrap_user_name: str = Field(min_length=1, max_length=120)
    bootstrap_organization_id: UUID
    bootstrap_organization_name: str = Field(min_length=1, max_length=120)
    bootstrap_organization_slug: str = Field(
        min_length=1,
        max_length=63,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    @model_validator(mode="after")
    def reject_bootstrap_auth_in_production(self) -> "Settings":
        if self.environment == "production":
            raise ValueError(
                "bootstrap authentication is development-only; configure production auth first"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
