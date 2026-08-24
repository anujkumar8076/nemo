from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status

from autodev_api.bootstrap import ensure_bootstrap_identity
from autodev_api.config import get_settings
from autodev_api.database import engine
from autodev_api.errors import install_error_handlers
from autodev_api.health import dependency_health
from autodev_api.routes import router, webhook_router
from autodev_api.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await ensure_bootstrap_identity(get_settings())
    yield
    await engine.dispose()


app = FastAPI(
    title="Autonomous Dev Team API",
    version="0.5.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)
install_error_handlers(app)
app.include_router(router)
app.include_router(webhook_router)


@app.middleware("http")
async def add_correlation_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request.state.correlation_id = uuid4()
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = str(request.state.correlation_id)
    return response


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
