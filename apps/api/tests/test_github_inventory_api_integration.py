import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from autodev_api.bootstrap import ensure_bootstrap_identity
from autodev_api.config import get_settings
from autodev_api.database import session_factory
from autodev_api.main import app
from autodev_api.models import (
    GitHubInstallation,
    GitHubInstallationRepository,
    Organization,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("AUTODEV_RUN_INTEGRATION") != "1",
        reason="set AUTODEV_RUN_INTEGRATION=1 against a migrated PostgreSQL database",
    ),
]


def installation(
    *, record_id: UUID, organization_id: UUID, external_id: int, login: str
) -> GitHubInstallation:
    return GitHubInstallation(
        id=record_id,
        organization_id=organization_id,
        external_id=external_id,
        account_external_id=external_id + 10_000,
        account_login=login,
        account_type="Organization",
        repository_selection="selected",
        permissions={"metadata": "read", "contents": "read"},
    )


def repository(
    *,
    organization_id: UUID,
    installation_id: UUID,
    external_id: int,
    available: bool,
) -> GitHubInstallationRepository:
    now = datetime.now(UTC)
    return GitHubInstallationRepository(
        organization_id=organization_id,
        installation_id=installation_id,
        external_id=external_id,
        node_id=f"R_{external_id}",
        owner="inventory-api",
        name=f"repo-{external_id}",
        full_name=f"inventory-api/repo-{external_id}",
        private=True,
        default_branch="main",
        html_url=f"https://github.com/inventory-api/repo-{external_id}",
        archived=False,
        disabled=False,
        available=available,
        last_seen_at=now,
        removed_at=None if available else now,
    )


@pytest.mark.asyncio
async def test_github_inventory_api_is_paginated_and_tenant_scoped() -> None:
    settings = get_settings()
    await ensure_bootstrap_identity(settings)
    first_installation_id = uuid4()
    second_installation_id = uuid4()
    other_organization_id = uuid4()
    other_installation_id = uuid4()
    unique_offset = uuid4().int % 1_000_000

    async with session_factory.begin() as session:
        session.add(
            Organization(
                id=other_organization_id,
                name="Inventory API isolation tenant",
                slug=f"inventory-api-{other_organization_id.hex[:12]}",
            )
        )
        await session.flush()
        session.add_all(
            [
                installation(
                    record_id=first_installation_id,
                    organization_id=settings.bootstrap_organization_id,
                    external_id=100_000_000 + unique_offset,
                    login="first-installation",
                ),
                installation(
                    record_id=second_installation_id,
                    organization_id=settings.bootstrap_organization_id,
                    external_id=110_000_000 + unique_offset,
                    login="second-installation",
                ),
                installation(
                    record_id=other_installation_id,
                    organization_id=other_organization_id,
                    external_id=120_000_000 + unique_offset,
                    login="other-tenant-installation",
                ),
            ]
        )
        await session.flush()
        session.add_all(
            [
                repository(
                    organization_id=settings.bootstrap_organization_id,
                    installation_id=first_installation_id,
                    external_id=201,
                    available=True,
                ),
                repository(
                    organization_id=settings.bootstrap_organization_id,
                    installation_id=first_installation_id,
                    external_id=202,
                    available=False,
                ),
                repository(
                    organization_id=other_organization_id,
                    installation_id=other_installation_id,
                    external_id=203,
                    available=True,
                ),
            ]
        )

    headers = {"Authorization": f"Bearer {settings.bootstrap_api_token.get_secret_value()}"}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as client:
        installations = await client.get("/v1/github/installations?limit=100")
        first_page = await client.get("/v1/github/installations?limit=1")
        available_repositories = await client.get(
            f"/v1/github/repositories?installation_id={first_installation_id}"
        )
        complete_inventory = await client.get(
            f"/v1/github/repositories?installation_id={first_installation_id}&include_removed=true"
        )
        other_tenant_inventory = await client.get(
            f"/v1/github/repositories?installation_id={other_installation_id}&include_removed=true"
        )
        invalid_cursor = await client.get("/v1/github/repositories?cursor=invalid")

    assert installations.status_code == 200
    installation_ids = {item["id"] for item in installations.json()["items"]}
    assert {str(first_installation_id), str(second_installation_id)} <= installation_ids
    assert str(other_installation_id) not in installation_ids
    assert first_page.status_code == 200
    assert first_page.json()["next_cursor"] is not None

    assert available_repositories.status_code == 200
    assert [item["external_id"] for item in available_repositories.json()["items"]] == [201]
    assert complete_inventory.status_code == 200
    assert {item["external_id"] for item in complete_inventory.json()["items"]} == {201, 202}
    assert other_tenant_inventory.status_code == 200
    assert other_tenant_inventory.json()["items"] == []
    assert invalid_cursor.status_code == 400
    assert invalid_cursor.json()["error"]["code"] == "invalid_cursor"
