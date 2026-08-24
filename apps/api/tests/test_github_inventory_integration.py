import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select, update

from autodev_api.bootstrap import ensure_bootstrap_identity
from autodev_api.config import get_settings
from autodev_api.database import session_factory
from autodev_api.github_client import GitHubRepository
from autodev_api.github_inventory import (
    GitHubInstallationUnavailableError,
    synchronize_installation_repositories,
)
from autodev_api.models import (
    GitHubInstallation,
    GitHubInstallationRepository,
    GitHubInstallationStatus,
    Organization,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("AUTODEV_RUN_INTEGRATION") != "1",
        reason="set AUTODEV_RUN_INTEGRATION=1 against a migrated PostgreSQL database",
    ),
]


def repository(identifier: int, *, default_branch: str = "main") -> GitHubRepository:
    return GitHubRepository.model_validate(
        {
            "id": identifier,
            "node_id": f"R_{identifier}",
            "owner": {"login": "octo-org"},
            "name": f"repo-{identifier}",
            "full_name": f"octo-org/repo-{identifier}",
            "private": True,
            "default_branch": default_branch,
            "html_url": f"https://github.com/octo-org/repo-{identifier}",
        }
    )


@pytest.mark.asyncio
async def test_repository_inventory_reconciles_removal_and_enforces_tenant() -> None:
    settings = get_settings()
    await ensure_bootstrap_identity(settings)
    installation_id = uuid4()
    other_organization_id = uuid4()
    synchronized_at = datetime.now(UTC)

    async with session_factory.begin() as session:
        session.add_all(
            [
                GitHubInstallation(
                    id=installation_id,
                    organization_id=settings.bootstrap_organization_id,
                    external_id=70_000_000 + uuid4().int % 1_000_000,
                    account_external_id=80_000_000 + uuid4().int % 1_000_000,
                    account_login="octo-org",
                    account_type="Organization",
                    repository_selection="selected",
                    permissions={"metadata": "read", "contents": "read"},
                ),
                Organization(
                    id=other_organization_id,
                    name="Inventory isolation tenant",
                    slug=f"inventory-isolation-{other_organization_id.hex[:10]}",
                ),
            ]
        )

    async with session_factory() as session:
        first = await synchronize_installation_repositories(
            session,
            organization_id=settings.bootstrap_organization_id,
            installation_id=installation_id,
            repositories=[repository(101), repository(102)],
            synchronized_at=synchronized_at,
        )
    assert first.available == 2
    assert first.removed == 0

    async with session_factory() as session:
        second = await synchronize_installation_repositories(
            session,
            organization_id=settings.bootstrap_organization_id,
            installation_id=installation_id,
            repositories=[repository(102, default_branch="trunk"), repository(103)],
            synchronized_at=synchronized_at + timedelta(minutes=1),
        )
    assert second.available == 2
    assert second.removed == 1

    async with session_factory() as session:
        inventory = list(
            (
                await session.scalars(
                    select(GitHubInstallationRepository)
                    .where(GitHubInstallationRepository.installation_id == installation_id)
                    .order_by(GitHubInstallationRepository.external_id)
                )
            ).all()
        )
        installation = await session.get(GitHubInstallation, installation_id)
    assert [item.external_id for item in inventory] == [101, 102, 103]
    assert inventory[0].available is False
    assert inventory[0].removed_at == synchronized_at + timedelta(minutes=1)
    assert inventory[1].available is True
    assert inventory[1].default_branch == "trunk"
    assert inventory[1].removed_at is None
    assert inventory[2].available is True
    assert installation is not None
    assert installation.last_synced_at == synchronized_at + timedelta(minutes=1)

    async with session_factory() as session:
        with pytest.raises(GitHubInstallationUnavailableError):
            await synchronize_installation_repositories(
                session,
                organization_id=other_organization_id,
                installation_id=installation_id,
                repositories=[repository(104)],
            )

    async with session_factory.begin() as session:
        await session.execute(
            update(GitHubInstallation)
            .where(GitHubInstallation.id == installation_id)
            .values(status=GitHubInstallationStatus.REVOKED)
        )
    async with session_factory() as session:
        with pytest.raises(GitHubInstallationUnavailableError):
            await synchronize_installation_repositories(
                session,
                organization_id=settings.bootstrap_organization_id,
                installation_id=installation_id,
                repositories=[repository(104)],
            )
