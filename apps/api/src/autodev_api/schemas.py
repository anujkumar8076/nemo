from typing import Literal

from pydantic import BaseModel


class DependencyStatus(BaseModel):
    status: Literal["available", "unavailable"]
    detail: str | None = None


class HealthResponse(BaseModel):
    service: Literal["api"] = "api"
    status: Literal["healthy", "degraded"]
    dependencies: dict[str, DependencyStatus] | None = None
