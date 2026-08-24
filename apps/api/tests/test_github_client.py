from datetime import UTC, datetime, timedelta

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr

from autodev_api.github_client import (
    GitHubAppClient,
    GitHubAppCredentials,
    GitHubRateLimitError,
)


def credentials() -> tuple[GitHubAppCredentials, bytes]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return GitHubAppCredentials(
        app_id=12345, private_key=SecretStr(private_pem.decode())
    ), public_pem


def token_response() -> dict[str, str]:
    return {
        "token": "ghs_12345_stateless-token-format-is-not-fixed-length",
        "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }


@pytest.mark.asyncio
async def test_installation_token_uses_short_lived_app_jwt_and_hides_token() -> None:
    app_credentials, public_key = credentials()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/app/installations/789/access_tokens"
        assert request.headers["X-GitHub-Api-Version"] == "2026-03-10"
        encoded_jwt = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(encoded_jwt, public_key, algorithms=["RS256"])
        assert claims["iss"] == "12345"
        assert claims["exp"] - claims["iat"] == 600
        return httpx.Response(201, json=token_response())

    async with GitHubAppClient(
        credentials=app_credentials,
        api_url="https://api.github.test",
        api_version="2026-03-10",
        transport=httpx.MockTransport(handler),
    ) as client:
        token = await client.installation_token(
            789,
            repository_ids=[987],
            permissions={"contents": "write", "pull_requests": "write"},
        )

    assert token.token.get_secret_value().startswith("ghs_")
    assert token.token.get_secret_value() not in repr(token)


@pytest.mark.asyncio
async def test_repository_listing_paginates_with_one_ephemeral_token() -> None:
    app_credentials, _ = credentials()
    token_requests = 0
    repository_requests = 0

    def repository(identifier: int) -> dict[str, object]:
        return {
            "id": identifier,
            "node_id": f"R_{identifier}",
            "name": f"repo-{identifier}",
            "full_name": f"owner/repo-{identifier}",
            "private": True,
            "default_branch": "main",
            "html_url": f"https://github.test/owner/repo-{identifier}",
        }

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal repository_requests, token_requests
        if request.url.path.endswith("/access_tokens"):
            token_requests += 1
            return httpx.Response(201, json=token_response())
        repository_requests += 1
        page = int(request.url.params["page"])
        items = [repository(1)] if page == 1 else [repository(2)]
        return httpx.Response(200, json={"total_count": 2, "repositories": items})

    async with GitHubAppClient(
        credentials=app_credentials,
        api_url="https://api.github.test",
        api_version="2026-03-10",
        transport=httpx.MockTransport(handler),
    ) as client:
        repositories = await client.list_installation_repositories(789)

    assert [repository.id for repository in repositories] == [1, 2]
    assert token_requests == 1
    assert repository_requests == 2


@pytest.mark.asyncio
async def test_rate_limit_error_is_typed_and_body_is_not_exposed() -> None:
    app_credentials, _ = credentials()
    reset = int((datetime.now(UTC) + timedelta(minutes=3)).timestamp())

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(reset)},
            json={"message": "provider body must not leak"},
        )

    async with GitHubAppClient(
        credentials=app_credentials,
        api_url="https://api.github.test",
        api_version="2026-03-10",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(GitHubRateLimitError) as error:
            await client.installation_token(789)

    assert error.value.retry_at is not None
    assert "provider body" not in str(error.value)
