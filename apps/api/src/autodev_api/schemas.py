from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DependencyStatus(BaseModel):
    status: Literal["available", "unavailable"]
    detail: str | None = None


class HealthResponse(BaseModel):
    service: Literal["api"] = "api"
    status: Literal["healthy", "degraded"]
    dependencies: dict[str, DependencyStatus] | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    correlation_id: UUID
    details: dict[str, Any] | list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ProjectCreate(BaseModel):
    client_request_id: UUID
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=1,
        max_length=63,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = Field(default=None, max_length=5000)


class ProjectUpdate(BaseModel):
    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    status: Literal["active", "archived"] | None = None

    @model_validator(mode="after")
    def require_change(self) -> "ProjectUpdate":
        mutable_fields = {"name", "description", "status"}
        if not self.model_fields_set.intersection(mutable_fields):
            raise ValueError("at least one mutable project field is required")
        return self


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    client_request_id: UUID
    name: str
    slug: str
    description: str | None
    status: Literal["active", "archived"]
    version: int
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime


class ProjectPage(BaseModel):
    items: list[ProjectRead]
    next_cursor: str | None = None


class TaskCreate(BaseModel):
    client_request_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=20_000)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    project_id: UUID
    client_request_id: UUID
    title: str
    description: str
    mode: Literal["build", "guardian"]
    status: Literal[
        "queued",
        "planning",
        "awaiting_approval",
        "running",
        "validating",
        "completed",
        "failed",
        "cancelled",
    ]
    created_by_user_id: UUID
    cancelled_by_user_id: UUID | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    project_id: UUID
    task_id: UUID | None
    actor_user_id: UUID | None
    event_type: str
    entity_type: str
    entity_id: UUID
    schema_version: int
    details: dict[str, Any]
    created_at: datetime


class ActivityPage(BaseModel):
    items: list[AuditEventRead]
    next_cursor: str | None = None


class GitHubInstallationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: int
    account_external_id: int
    account_login: str
    account_type: Literal["Organization", "User"]
    repository_selection: Literal["all", "selected"]
    permissions: dict[str, Any]
    status: Literal["active", "suspended", "revoked"]
    suspended_at: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GitHubInstallationPage(BaseModel):
    items: list[GitHubInstallationRead]
    next_cursor: str | None = None


class GitHubRepositoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    installation_id: UUID
    external_id: int
    owner: str
    name: str
    full_name: str
    private: bool
    default_branch: str
    html_url: str
    archived: bool
    disabled: bool
    available: bool
    last_seen_at: datetime
    removed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GitHubRepositoryPage(BaseModel):
    items: list[GitHubRepositoryRead]
    next_cursor: str | None = None


class GitHubWebhookAccepted(BaseModel):
    status: Literal["accepted", "duplicate", "ignored"]
    delivery_id: str
