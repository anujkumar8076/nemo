import os
from datetime import UTC, datetime, timedelta

import pytest

from autodev_api.bootstrap import ensure_bootstrap_identity
from autodev_api.config import get_settings
from autodev_api.database import session_factory
from autodev_api.github_claims import (
    InvalidGitHubClaimStateError,
    VerifiedGitHubInstallation,
    begin_installation_claim,
    complete_verified_installation_claim,
    record_setup_installation,
    state_digest,
)
from autodev_api.models import GitHubInstallationClaim, GitHubInstallationClaimStatus

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("AUTODEV_RUN_INTEGRATION") != "1",
        reason="set AUTODEV_RUN_INTEGRATION=1 against a migrated PostgreSQL database",
    ),
]


@pytest.mark.asyncio
async def test_claim_state_is_hashed_bound_and_consumed_after_verified_identity() -> None:
    settings = get_settings()
    await ensure_bootstrap_identity(settings)
    issued_at = datetime.now(UTC)

    async with session_factory() as session:
        started = await begin_installation_claim(
            session,
            organization_id=settings.bootstrap_organization_id,
            user_id=settings.bootstrap_user_id,
            now=issued_at,
        )
    raw_state = started.state.get_secret_value()
    assert raw_state not in repr(started)

    async with session_factory() as session:
        stored = await session.get(GitHubInstallationClaim, started.claim_id)
    assert stored is not None
    assert stored.state_digest == state_digest(raw_state)
    assert raw_state != stored.state_digest
    assert stored.organization_id == settings.bootstrap_organization_id
    assert stored.initiated_by_user_id == settings.bootstrap_user_id

    async with session_factory() as session:
        awaiting_user = await record_setup_installation(
            session,
            raw_state=raw_state,
            installation_external_id=765_432_101,
            now=issued_at + timedelta(minutes=1),
        )
    assert awaiting_user.status == GitHubInstallationClaimStatus.AWAITING_AUTHORIZATION

    async with session_factory() as session:
        repeated = await record_setup_installation(
            session,
            raw_state=raw_state,
            installation_external_id=765_432_101,
            now=issued_at + timedelta(minutes=2),
        )
    assert repeated.id == started.claim_id

    async with session_factory() as session:
        with pytest.raises(InvalidGitHubClaimStateError):
            await record_setup_installation(
                session,
                raw_state=raw_state,
                installation_external_id=765_432_102,
                now=issued_at + timedelta(minutes=2),
            )

    proof = VerifiedGitHubInstallation(
        installation_external_id=765_432_101,
        account_external_id=876_543_201,
        account_login="verified-octo-org",
        account_type="Organization",
        repository_selection="selected",
        permissions={"metadata": "read", "contents": "read"},
        verified_user_external_id=987_654_301,
        verified_user_login="verified-installer",
    )
    async with session_factory() as session:
        installation = await complete_verified_installation_claim(
            session,
            raw_state=raw_state,
            verified=proof,
            now=issued_at + timedelta(minutes=3),
        )
    assert installation.organization_id == settings.bootstrap_organization_id
    assert installation.external_id == proof.installation_external_id

    async with session_factory() as session:
        completed = await session.get(GitHubInstallationClaim, started.claim_id)
    assert completed is not None
    assert completed.status == GitHubInstallationClaimStatus.COMPLETED
    assert completed.consumed_at == issued_at + timedelta(minutes=3)
    assert completed.verified_github_user_external_id == proof.verified_user_external_id
    assert completed.verified_github_user_login == proof.verified_user_login

    async with session_factory() as session:
        with pytest.raises(InvalidGitHubClaimStateError):
            await complete_verified_installation_claim(
                session,
                raw_state=raw_state,
                verified=proof,
                now=issued_at + timedelta(minutes=4),
            )


@pytest.mark.asyncio
async def test_expired_claim_state_cannot_record_spoofed_setup_identifier() -> None:
    settings = get_settings()
    await ensure_bootstrap_identity(settings)
    issued_at = datetime.now(UTC)
    async with session_factory() as session:
        started = await begin_installation_claim(
            session,
            organization_id=settings.bootstrap_organization_id,
            user_id=settings.bootstrap_user_id,
            now=issued_at,
            lifetime=timedelta(minutes=1),
        )

    async with session_factory() as session:
        with pytest.raises(InvalidGitHubClaimStateError):
            await record_setup_installation(
                session,
                raw_state=started.state.get_secret_value(),
                installation_external_id=765_432_999,
                now=issued_at + timedelta(minutes=2),
            )
