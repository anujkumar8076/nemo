import hashlib
import hmac
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr, ValidationError

from autodev_api.config import Settings
from autodev_api.errors import ApiError
from autodev_api.github_webhooks import verify_signature
from autodev_api.main import app
from autodev_api.schemas import ProjectUpdate
from autodev_api.services import decode_cursor, encode_cursor


@pytest.mark.asyncio
async def test_platform_routes_require_authentication() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/projects")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
    assert response.headers["x-correlation-id"] == response.json()["error"]["correlation_id"]


@pytest.mark.asyncio
async def test_unknown_routes_use_the_error_envelope() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.headers["x-correlation-id"] == response.json()["error"]["correlation_id"]


def test_project_update_requires_a_mutable_field() -> None:
    with pytest.raises(ValidationError, match="at least one mutable project field"):
        ProjectUpdate(expected_version=1)


def test_bootstrap_auth_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError, match="development-only"):
        Settings(
            environment="production",
            database_url="postgresql+psycopg://example.invalid/autodev",
            redis_url="redis://example.invalid/0",
            temporal_address="example.invalid:7233",
            bootstrap_api_token=SecretStr("a" * 32),
            bootstrap_user_id=uuid4(),
            bootstrap_user_email="developer@example.invalid",
            bootstrap_user_name="Developer",
            bootstrap_organization_id=uuid4(),
            bootstrap_organization_name="Workspace",
            bootstrap_organization_slug="workspace",
        )


def test_github_remote_actions_require_app_credentials() -> None:
    with pytest.raises(ValidationError, match="app ID, and private key"):
        Settings(
            database_url="postgresql+psycopg://example.invalid/autodev",
            redis_url="redis://example.invalid/0",
            temporal_address="example.invalid:7233",
            bootstrap_api_token=SecretStr("a" * 32),
            bootstrap_user_id=uuid4(),
            bootstrap_user_email="developer@example.invalid",
            bootstrap_user_name="Developer",
            bootstrap_organization_id=uuid4(),
            bootstrap_organization_name="Workspace",
            bootstrap_organization_slug="workspace",
            github_integration_enabled=True,
            github_webhook_secret=SecretStr("b" * 32),
            github_remote_actions_enabled=True,
        )


def test_cursor_round_trip_and_rejects_invalid_values() -> None:
    created_at = datetime(2026, 8, 24, 12, 30, tzinfo=UTC)
    record_id = UUID("00000000-0000-4000-8000-000000000003")

    assert decode_cursor(encode_cursor(created_at, record_id)) == (created_at, record_id)
    with pytest.raises(ApiError) as error:
        decode_cursor("not-a-cursor")
    assert error.value.code == "invalid_cursor"


def test_github_signature_verification_uses_the_raw_body() -> None:
    body = '{"zen":"Keep it logically awesome ✓"}'.encode()
    secret = "webhook-test-secret-with-at-least-32-characters"
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    verify_signature(body, signature, secret)
    with pytest.raises(ApiError) as error:
        verify_signature(body + b" ", signature, secret)
    assert error.value.code == "invalid_webhook_signature"
