from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class GitHubClientError(Exception):
    """Sanitized provider error safe to record without credentials or response bodies."""


class GitHubRateLimitError(GitHubClientError):
    def __init__(self, retry_at: datetime | None) -> None:
        super().__init__("GitHub API rate limit exceeded")
        self.retry_at = retry_at


class GitHubRepositoryOwner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str


class GitHubRepository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    node_id: str
    owner: GitHubRepositoryOwner
    name: str
    full_name: str
    private: bool
    default_branch: str
    html_url: str
    archived: bool = False
    disabled: bool = False


class InstallationTokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: SecretStr
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class GitHubAppCredentials:
    app_id: int
    private_key: SecretStr

    def create_jwt(self, now: datetime | None = None) -> str:
        issued_at = (now or datetime.now(UTC)).astimezone(UTC)
        return jwt.encode(
            {
                "iat": int((issued_at - timedelta(seconds=60)).timestamp()),
                "exp": int((issued_at + timedelta(minutes=9)).timestamp()),
                "iss": str(self.app_id),
            },
            self.private_key.get_secret_value(),
            algorithm="RS256",
        )


def retry_time(response: httpx.Response) -> datetime | None:
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        try:
            return datetime.now(UTC) + timedelta(seconds=max(0, int(retry_after)))
        except ValueError:
            pass
    reset = response.headers.get("X-RateLimit-Reset")
    if reset is not None:
        try:
            return datetime.fromtimestamp(int(reset), tz=UTC)
        except (ValueError, OSError):
            pass
    return None


class GitHubAppClient:
    def __init__(
        self,
        *,
        credentials: GitHubAppCredentials,
        api_url: str,
        api_version: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._credentials = credentials
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

    async def __aenter__(self) -> "GitHubAppClient":
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self._client.aclose()

    async def installation_token(
        self,
        installation_id: int,
        *,
        repository_ids: list[int] | None = None,
        permissions: dict[str, str] | None = None,
    ) -> InstallationTokenResponse:
        if installation_id <= 0:
            raise ValueError("installation_id must be positive")
        request_body: dict[str, Any] = {}
        if repository_ids is not None:
            if not repository_ids or len(repository_ids) > 500:
                raise ValueError("repository_ids must contain between 1 and 500 entries")
            request_body["repository_ids"] = repository_ids
        if permissions is not None:
            request_body["permissions"] = permissions
        response = await self._client.post(
            f"/app/installations/{installation_id}/access_tokens",
            headers={"Authorization": f"Bearer {self._credentials.create_jwt()}"},
            json=request_body,
        )
        self._raise_for_provider_error(response)
        try:
            token = InstallationTokenResponse.model_validate(response.json())
        except (ValueError, TypeError) as error:
            raise GitHubClientError(
                "GitHub returned an invalid installation token response"
            ) from error
        if token.expires_at <= datetime.now(UTC):
            raise GitHubClientError("GitHub returned an expired installation token")
        return token

    async def list_installation_repositories(self, installation_id: int) -> list[GitHubRepository]:
        token = await self.installation_token(installation_id)
        repositories: list[GitHubRepository] = []
        page = 1
        while True:
            response = await self._client.get(
                "/installation/repositories",
                headers={"Authorization": f"Bearer {token.token.get_secret_value()}"},
                params={"per_page": 100, "page": page},
            )
            self._raise_for_provider_error(response)
            try:
                value = response.json()
                raw_repositories = value.get("repositories") if isinstance(value, dict) else None
                total_count = value.get("total_count") if isinstance(value, dict) else None
                if not isinstance(raw_repositories, list) or not isinstance(total_count, int):
                    raise TypeError
                repositories.extend(
                    GitHubRepository.model_validate(item) for item in raw_repositories
                )
            except (ValueError, TypeError) as error:
                raise GitHubClientError("GitHub returned an invalid repository list") from error
            if len(repositories) >= total_count:
                return repositories
            if not raw_repositories:
                raise GitHubClientError("GitHub repository pagination ended before total_count")
            page += 1

    @staticmethod
    def _raise_for_provider_error(response: httpx.Response) -> None:
        if response.status_code in {403, 429} and (
            response.status_code == 429
            or response.headers.get("X-RateLimit-Remaining") == "0"
            or "Retry-After" in response.headers
        ):
            raise GitHubRateLimitError(retry_time(response))
        if response.is_error:
            raise GitHubClientError(f"GitHub API request failed with status {response.status_code}")
