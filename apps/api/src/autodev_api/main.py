from fastapi import FastAPI, Response, status

from autodev_api.config import get_settings
from autodev_api.health import dependency_health
from autodev_api.schemas import HealthResponse

app = FastAPI(
    title="Autonomous Dev Team API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def liveness() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
async def readiness(response: Response) -> HealthResponse:
    dependencies = await dependency_health(get_settings())
    healthy = all(item.status == "available" for item in dependencies.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="healthy" if healthy else "degraded",
        dependencies=dependencies,
    )
