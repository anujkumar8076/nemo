from urllib.parse import parse_qs

import httpx
import pytest
from pydantic import SecretStr

from autodev_api.github_client import GitHubClientError
from autodev_api.github_user_client import (
    GitHubInstallationVerificationError,
    GitHubOAuthCredentials,
    GitHubUserAuthorizationClient,
)


def installation(identifier: int) -> dict[str, object]:
    return {
        "id": identifier,
        "account": {
            "id": 500 + identifier,
            "login": f"octo-org-{identifier}",
            "type": "Organization",
        },
        "repository_selection": "selected",
        "permissions": {"metadata": "read", "contents": "read"},
    }


def client(
    handler: httpx.MockTransport,
) -> GitHubUserAuthorizationClient:
    return GitHubUserAuthorizationClient(
        credentials=GitHubOAuthCredentials(
            client_id="Iv1.test-client",
            client_secret=SecretStr("oauth-client-secret"),
            callback_url="https://control.test/github/callback",
        ),
        api_url="https://api.github.test",
        oauth_url="https://github.test",
        api_version="2026-03-10",
        transport=handler,
    )


@pytest.mark.asyncio
async def test_user_authorization_verifies_exact_accessible_installation_and_discards_token() -> (
    None
):
    token_requests = 0
    installation_requests = 0
    opaque_token = "ghu_opaque-user-token-never-returned"

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal installation_requests, token_requests
        if request.url.path == "/login/oauth/access_token":
            token_requests += 1
            form = parse_qs(request.content.decode())
            assert form["client_id"] == ["Iv1.test-client"]
            assert form["client_secret"] == ["oauth-client-secret"]
            assert form["code"] == ["one-time-code"]
            assert form["redirect_uri"] == ["https://control.test/github/callback"]
            return httpx.Response(
                200,
                json={"access_token": opaque_token, "token_type": "bearer"},
            )
        assert request.headers["Authorization"] == f"Bearer {opaque_token}"
        assert request.headers["X-GitHub-Api-Version"] == "2026-03-10"
        if request.url.path == "/user":
            return httpx.Response(200, json={"id": 321, "login": "verified-user"})
        installation_requests += 1
        page = int(request.url.params["page"])
        items = [installation(101)] if page == 1 else [installation(202)]
        return httpx.Response(200, json={"total_count": 2, "installations": items})

    async with client(httpx.MockTransport(handler)) as authorization:
        proof = await authorization.verify_installation(
            code="one-time-code",
            installation_external_id=202,
        )

    assert proof.installation_external_id == 202
    assert proof.account_login == "octo-org-202"
    assert proof.verified_user_external_id == 321
    assert proof.verified_user_login == "verified-user"
    assert opaque_token not in repr(proof)
    assert token_requests == 1
    assert installation_requests == 2


@pytest.mark.asyncio
async def test_user_authorization_rejects_installation_not_accessible_to_user() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/login/oauth/access_token":
            return httpx.Response(
                200,
                json={"access_token": "ghu_ephemeral", "token_type": "bearer"},
            )
        if request.url.path == "/user":
            return httpx.Response(200, json={"id": 321, "login": "verified-user"})
        return httpx.Response(200, json={"total_count": 1, "installations": [installation(101)]})

    async with client(httpx.MockTransport(handler)) as authorization:
        with pytest.raises(GitHubInstallationVerificationError, match="cannot verify"):
            await authorization.verify_installation(
                code="one-time-code",
                installation_external_id=999,
            )


@pytest.mark.asyncio
async def test_oauth_error_payload_is_sanitized() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"error": "bad_verification_code", "error_description": "must not leak"},
        )

    async with client(httpx.MockTransport(handler)) as authorization:
        with pytest.raises(GitHubClientError) as error:
            await authorization.exchange_code("invalid-code")

    assert "must not leak" not in str(error.value)
