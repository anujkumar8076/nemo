import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.models import (
    GitHubInstallation,
    GitHubInstallationClaim,
    GitHubInstallationClaimStatus,
    GitHubInstallationStatus,
)


class InvalidGitHubClaimStateError(Exception):
    """The one-time installation claim is invalid, expired, or already consumed."""


@dataclass(frozen=True, slots=True)
class InstallationClaimStart:
    claim_id: UUID
    state: SecretStr
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class VerifiedGitHubInstallation:
    installation_external_id: int
    account_external_id: int
    account_login: str
    account_type: str
    repository_selection: str
    permissions: dict[str, Any]
    verified_user_external_id: int
    verified_user_login: str


def state_digest(state: str) -> str:
    return hashlib.sha256(state.encode()).hexdigest()


async def begin_installation_claim(
    session: AsyncSession,
    *,
    organization_id: UUID,
    user_id: UUID,
    now: datetime | None = None,
    lifetime: timedelta = timedelta(minutes=10),
) -> InstallationClaimStart:
    if lifetime <= timedelta(0) or lifetime > timedelta(minutes=30):
        raise ValueError("claim lifetime must be greater than zero and at most 30 minutes")
    issued_at = (now or datetime.now(UTC)).astimezone(UTC)
    raw_state = secrets.token_urlsafe(32)
    claim = GitHubInstallationClaim(
        organization_id=organization_id,
        initiated_by_user_id=user_id,
        state_digest=state_digest(raw_state),
        expires_at=issued_at + lifetime,
    )
    session.add(claim)
    await session.commit()
    await session.refresh(claim)
    return InstallationClaimStart(
        claim_id=claim.id,
        state=SecretStr(raw_state),
        expires_at=claim.expires_at,
    )


async def _lock_claim(
    session: AsyncSession,
    *,
    raw_state: str,
    now: datetime,
) -> GitHubInstallationClaim:
    claim = await session.scalar(
        select(GitHubInstallationClaim)
        .where(GitHubInstallationClaim.state_digest == state_digest(raw_state))
        .with_for_update()
    )
    if claim is None or claim.expires_at <= now or claim.consumed_at is not None:
        raise InvalidGitHubClaimStateError("Installation claim state is invalid")
    return claim


async def record_setup_installation(
    session: AsyncSession,
    *,
    raw_state: str,
    installation_external_id: int,
    now: datetime | None = None,
) -> GitHubInstallationClaim:
    if installation_external_id <= 0:
        raise ValueError("installation_external_id must be positive")
    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    claim = await _lock_claim(session, raw_state=raw_state, now=checked_at)
    if claim.status == GitHubInstallationClaimStatus.AWAITING_SETUP:
        claim.installation_external_id = installation_external_id
        claim.status = GitHubInstallationClaimStatus.AWAITING_AUTHORIZATION
    elif (
        claim.status != GitHubInstallationClaimStatus.AWAITING_AUTHORIZATION
        or claim.installation_external_id != installation_external_id
    ):
        raise InvalidGitHubClaimStateError("Installation claim state is invalid")
    await session.commit()
    await session.refresh(claim)
    return claim


async def complete_verified_installation_claim(
    session: AsyncSession,
    *,
    raw_state: str,
    verified: VerifiedGitHubInstallation,
    now: datetime | None = None,
) -> GitHubInstallation:
    if (
        verified.installation_external_id <= 0
        or verified.account_external_id <= 0
        or verified.verified_user_external_id <= 0
        or not verified.account_login
        or not verified.verified_user_login
        or verified.account_type not in {"Organization", "User"}
        or verified.repository_selection not in {"all", "selected"}
    ):
        raise ValueError("verified GitHub installation proof is invalid")
    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    claim = await _lock_claim(session, raw_state=raw_state, now=checked_at)
    if (
        claim.status != GitHubInstallationClaimStatus.AWAITING_AUTHORIZATION
        or claim.installation_external_id != verified.installation_external_id
    ):
        raise InvalidGitHubClaimStateError("Installation claim state is invalid")

    installation = await session.scalar(
        select(GitHubInstallation)
        .where(GitHubInstallation.external_id == verified.installation_external_id)
        .with_for_update()
    )
    if installation is not None and installation.organization_id != claim.organization_id:
        raise InvalidGitHubClaimStateError("Installation claim state is invalid")
    if installation is None:
        installation = GitHubInstallation(
            organization_id=claim.organization_id,
            external_id=verified.installation_external_id,
            account_external_id=verified.account_external_id,
            account_login=verified.account_login,
            account_type=verified.account_type,
            repository_selection=verified.repository_selection,
            permissions=verified.permissions,
        )
        session.add(installation)
    else:
        installation.account_external_id = verified.account_external_id
        installation.account_login = verified.account_login
        installation.account_type = verified.account_type
        installation.repository_selection = verified.repository_selection
        installation.permissions = verified.permissions
        installation.status = GitHubInstallationStatus.ACTIVE
        installation.suspended_at = None

    claim.status = GitHubInstallationClaimStatus.COMPLETED
    claim.verified_github_user_external_id = verified.verified_user_external_id
    claim.verified_github_user_login = verified.verified_user_login
    claim.consumed_at = checked_at
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise InvalidGitHubClaimStateError("Installation claim state is invalid") from error
    await session.refresh(installation)
    return installation
