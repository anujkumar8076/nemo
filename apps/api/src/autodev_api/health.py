import asyncio
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from temporalio.client import Client
from temporalio.service import RPCError

from autodev_api.config import Settings
from autodev_api.schemas import DependencyStatus

HealthCheck = Callable[[], Awaitable[None]]


async def _database_check(settings: Settings) -> None:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    finally:
        await engine.dispose()


async def _redis_check(settings: Settings) -> None:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.ping()
    finally:
        await client.aclose()


async def _temporal_check(settings: Settings) -> None:
    await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)


async def _run_check(check: HealthCheck) -> DependencyStatus:
    try:
        await asyncio.wait_for(check(), timeout=2)
    except (TimeoutError, OSError, ConnectionError, RedisError, SQLAlchemyError, RPCError) as error:
        return DependencyStatus(status="unavailable", detail=type(error).__name__)
    return DependencyStatus(status="available")


async def dependency_health(settings: Settings) -> dict[str, DependencyStatus]:
    database, redis, temporal = await asyncio.gather(
        _run_check(lambda: _database_check(settings)),
        _run_check(lambda: _redis_check(settings)),
        _run_check(lambda: _temporal_check(settings)),
    )
    return {"postgresql": database, "redis": redis, "temporal": temporal}
