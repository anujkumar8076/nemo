from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch, mark

from autodev_api import main
from autodev_api.config import Settings
from autodev_api.main import app
from autodev_api.schemas import DependencyStatus


@mark.asyncio
async def test_liveness_does_not_depend_on_external_services() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "api",
        "status": "healthy",
        "dependencies": None,
    }


@mark.asyncio
async def test_readiness_reports_degraded_dependencies(monkeypatch: MonkeyPatch) -> None:
    async def unavailable_dependencies(_settings: Settings) -> dict[str, DependencyStatus]:
        return {
            "postgresql": DependencyStatus(status="available"),
            "redis": DependencyStatus(status="unavailable", detail="ConnectionError"),
            "temporal": DependencyStatus(status="available"),
        }

    monkeypatch.setattr(main, "dependency_health", unavailable_dependencies)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["dependencies"]["redis"]["status"] == "unavailable"
