from dataclasses import dataclass
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from autodev_api.github_claims import VerifiedGitHubInstallation
from autodev_api.github_client import GitHubClientError, raise_for_provider_error


class GitHubInstallationVerificationError(GitHubClientError):
    """The authorized GitHub user cannot prove access to the candidate installation."""


class GitHubUserAccessToken(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: SecretStr
    token_type: Literal["bearer"]


class GitHubUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    login: str = Field(min_length=1, max_length=255)


class GitHubInstallationAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    login: str = Field(min_length=1, max_length=255)
    type: Literal["Organization", "User"]


class GitHubUserInstallation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    account: GitHubInstallationAccount
    repository_selection: Literal["all", "selected"]
    permissions: dict[str, str]


@dataclass(frozen=True, slots=True)
class GitHubOAuthCredentials:
    client_id: str
    client_secret: SecretStr
    callback_url: str


class GitHubUserAuthorizationClient:
    def __init__(
        self,
        *,
        credentials: GitHubOAuthCredentials,
        api_url: str,
        oauth_url: str,
        api_version: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._credentials = credentials
        self._oauth_url = oauth_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=api_url,
            timeout=httpx.Timeout(10.0, connect=5.0),
            transport=transport,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "autonomous-dev-team-control-plane",
                "X-GitHub-Api-Version": api_version,
            },
        )

    async def __aenter__(self) -> "GitHubUserAuthorizationClient":
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self._client.aclose()

    async def exchange_code(self, code: str) -> GitHubUserAccessToken:
        if not code or len(code) > 1024:
            raise ValueError("OAuth code must contain between 1 and 1024 characters")
        response = await self._client.post(
            f"{self._oauth_url}/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret.get_secret_value(),
                "code": code,
                "redirect_uri": self._credentials.callback_url,
            },
        )
        raise_for_provider_error(response)
        try:
            return GitHubUserAccessToken.model_validate(response.json())
        except (ValueError, TypeError) as error:
            raise GitHubClientError(
                "GitHub returned an invalid user access token response"
            ) from error

    async def authenticated_user(self, token: SecretStr) -> GitHubUser:
        response = await self._client.get(
            "/user",
            headers={"Authorization": f"Bearer {token.get_secret_value()}"},
        )
        raise_for_provider_error(response)
        try:
            return GitHubUser.model_validate(response.json())
        except (ValueError, TypeError) as error:
            raise GitHubClientError("GitHub returned an invalid authenticated user") from error

    async def user_installations(self, token: SecretStr) -> list[GitHubUserInstallation]:
        installations: list[GitHubUserInstallation] = []
        page = 1
        while True:
            response = await self._client.get(
                "/user/installations",
                headers={"Authorization": f"Bearer {token.get_secret_value()}"},
                params={"per_page": 100, "page": page},
            )
            raise_for_provider_error(response)
            try:
                value = response.json()
                raw_installations = value.get("installations") if isinstance(value, dict) else None
                total_count = value.get("total_count") if isinstance(value, dict) else None
                if (
                    not isinstance(raw_installations, list)
                    or not isinstance(total_count, int)
                    or isinstance(total_count, bool)
                ):
                    raise TypeError
                installations.extend(
                    GitHubUserInstallation.model_validate(item) for item in raw_installations
                )
            except (ValueError, TypeError) as error:
                raise GitHubClientError(
                    "GitHub returned an invalid user installation list"
                ) from error
            if len(installations) >= total_count:
                return installations
            if not raw_installations:
                raise GitHubClientError("GitHub user installation pagination ended early")
            page += 1

    async def verify_installation(
        self,
        *,
        code: str,
        installation_external_id: int,
    ) -> VerifiedGitHubInstallation:
        if installation_external_id <= 0:
            raise ValueError("installation_external_id must be positive")
        token_response = await self.exchange_code(code)
        user = await self.authenticated_user(token_response.access_token)
        installations = await self.user_installations(token_response.access_token)
        installation = next(
            (item for item in installations if item.id == installation_external_id),
            None,
        )
        if installation is None:
            raise GitHubInstallationVerificationError(
                "GitHub user cannot verify the requested installation"
            )
        return VerifiedGitHubInstallation(
            installation_external_id=installation.id,
            account_external_id=installation.account.id,
            account_login=installation.account.login,
            account_type=installation.account.type,
            repository_selection=installation.repository_selection,
            permissions=installation.permissions,
            verified_user_external_id=user.id,
            verified_user_login=user.login,
        )
