from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse
from uuid import UUID

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated server configuration loaded from AUTODEV_* variables."""

    model_config = SettingsConfigDict(
        env_prefix="AUTODEV_",
        env_file=".env",
        env_ignore_empty=True,
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
    github_integration_enabled: bool = False
    github_webhook_secret: SecretStr | None = None
    github_webhook_max_body_bytes: int = Field(default=2_000_000, ge=1024, le=25_000_000)
    github_remote_actions_enabled: bool = False
    github_app_id: int | None = Field(default=None, gt=0)
    github_private_key: SecretStr | None = None
    github_api_url: str = "https://api.github.com"
    github_api_version: str = "2026-03-10"
    github_user_authorization_enabled: bool = False
    github_client_id: str | None = Field(default=None, min_length=1, max_length=255)
    github_client_secret: SecretStr | None = None
    github_oauth_url: str = "https://github.com"
    github_oauth_callback_url: str | None = None
    github_installation_url: str | None = None

    @model_validator(mode="after")
    def reject_bootstrap_auth_in_production(self) -> "Settings":
        if self.environment == "production":
            raise ValueError(
                "bootstrap authentication is development-only; configure production auth first"
            )
        if self.github_integration_enabled and (
            self.github_webhook_secret is None
            or len(self.github_webhook_secret.get_secret_value()) < 32
        ):
            raise ValueError(
                "enabled GitHub integration requires a webhook secret of at least 32 characters"
            )
        if self.github_remote_actions_enabled and (
            not self.github_integration_enabled
            or self.github_app_id is None
            or self.github_private_key is None
        ):
            raise ValueError("GitHub remote actions require integration, app ID, and private key")
        if self.github_user_authorization_enabled:
            required = (
                self.github_integration_enabled,
                self.github_app_id is not None,
                self.github_private_key is not None,
                self.github_client_id is not None,
                self.github_client_secret is not None,
                self.github_oauth_callback_url is not None,
                self.github_installation_url is not None,
            )
            if not all(required):
                raise ValueError(
                    "GitHub user authorization requires integration, App credentials, "
                    "OAuth credentials, callback URL, and installation URL"
                )
            for name, value in (
                ("API URL", self.github_api_url),
                ("oauth URL", self.github_oauth_url),
                ("callback URL", self.github_oauth_callback_url),
                ("installation URL", self.github_installation_url),
            ):
                parsed = urlparse(value or "")
                if (
                    parsed.scheme != "https"
                    or parsed.hostname is None
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.query
                    or parsed.fragment
                ):
                    raise ValueError(
                        f"GitHub {name} must be an HTTPS URL without credentials, "
                        "query, or fragment"
                    )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
