import hashlib
import hmac
import json
import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from autodev_api.bootstrap import ensure_bootstrap_identity
from autodev_api.config import get_settings
from autodev_api.database import session_factory
from autodev_api.main import app
from autodev_api.models import Membership, MembershipRole, Organization, Project, User

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("AUTODEV_RUN_INTEGRATION") != "1",
        reason="set AUTODEV_RUN_INTEGRATION=1 against a migrated PostgreSQL database",
    ),
]


@pytest.mark.asyncio
async def test_persisted_project_task_and_activity_lifecycle() -> None:
    settings = get_settings()
    await ensure_bootstrap_identity(settings)
    headers = {"Authorization": f"Bearer {settings.bootstrap_api_token.get_secret_value()}"}
    project_request_id = uuid4()
    project_slug = f"integration-{uuid4().hex[:12]}"
    project_payload = {
        "client_request_id": str(project_request_id),
        "name": "Integration project",
        "slug": project_slug,
        "description": "A persisted Phase 1 integration test.",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as client:
        created_project = await client.post("/v1/projects", json=project_payload)
        assert created_project.status_code == 201, created_project.text
        project = created_project.json()
        project_id = project["id"]

        repeated_project = await client.post("/v1/projects", json=project_payload)
        assert repeated_project.status_code == 200
        assert repeated_project.json()["id"] == project_id

        conflicting_retry = await client.post(
            "/v1/projects",
            json={**project_payload, "name": "A different payload"},
        )
        assert conflicting_retry.status_code == 409
        assert conflicting_retry.json()["error"]["code"] == "idempotency_conflict"

        fetched_project = await client.get(f"/v1/projects/{project_id}")
        assert fetched_project.status_code == 200
        assert fetched_project.json()["slug"] == project_slug

        updated_project = await client.patch(
            f"/v1/projects/{project_id}",
            json={"expected_version": 1, "description": "Updated safely."},
        )
        assert updated_project.status_code == 200
        assert updated_project.json()["version"] == 2

        stale_update = await client.patch(
            f"/v1/projects/{project_id}",
            json={"expected_version": 1, "name": "Stale write"},
        )
        assert stale_update.status_code == 409
        assert stale_update.json()["error"]["code"] == "version_conflict"

        task_payload = {
            "client_request_id": str(uuid4()),
            "title": "Build the first reliable slice",
            "description": "Persist and expose the task lifecycle.",
        }
        created_task = await client.post(f"/v1/projects/{project_id}/tasks", json=task_payload)
        assert created_task.status_code == 201, created_task.text
        task_id = created_task.json()["id"]

        fetched_task = await client.get(f"/v1/tasks/{task_id}")
        assert fetched_task.status_code == 200
        assert fetched_task.json()["status"] == "queued"

        cancelled_task = await client.post(f"/v1/tasks/{task_id}/cancel")
        assert cancelled_task.status_code == 200
        assert cancelled_task.json()["status"] == "cancelled"
        assert (await client.post(f"/v1/tasks/{task_id}/cancel")).status_code == 200

        activity = await client.get(f"/v1/projects/{project_id}/activity")
        assert activity.status_code == 200
        event_types = {item["event_type"] for item in activity.json()["items"]}
        assert {
            "project.created",
            "project.updated",
            "task.created",
            "task.cancelled",
        } <= event_types

        invalid_cursor = await client.get("/v1/projects?cursor=invalid")
        assert invalid_cursor.status_code == 400
        assert invalid_cursor.json()["error"]["code"] == "invalid_cursor"

        other_user_id = uuid4()
        other_organization_id = uuid4()
        other_project_id = uuid4()
        async with session_factory.begin() as session:
            session.add_all(
                [
                    User(
                        id=other_user_id,
                        email=f"{other_user_id}@example.invalid",
                        display_name="Other tenant user",
                    ),
                    Organization(
                        id=other_organization_id,
                        name="Other tenant",
                        slug=f"other-{other_organization_id.hex[:12]}",
                    ),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    Membership(
                        organization_id=other_organization_id,
                        user_id=other_user_id,
                        role=MembershipRole.OWNER,
                    ),
                    Project(
                        id=other_project_id,
                        organization_id=other_organization_id,
                        client_request_id=uuid4(),
                        name="Other tenant project",
                        slug=f"other-project-{other_project_id.hex[:8]}",
                        created_by_user_id=other_user_id,
                    ),
                ]
            )

        cross_tenant_read = await client.get(f"/v1/projects/{other_project_id}")
        assert cross_tenant_read.status_code == 404
        assert cross_tenant_read.json()["error"]["code"] == "project_not_found"


@pytest.mark.asyncio
async def test_signed_github_delivery_is_persisted_and_deduplicated() -> None:
    secret = "github-webhook-integration-secret-000000000000"
    settings = get_settings().model_copy(
        update={
            "github_integration_enabled": True,
            "github_webhook_secret": SecretStr(secret),
        }
    )
    app.dependency_overrides[get_settings] = lambda: settings
    body = json.dumps(
        {
            "action": "opened",
            "installation": {"id": 12345678901},
            "repository": {"id": 98765432101},
            "issue": {"number": 7},
        },
        separators=(",", ":"),
    ).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Delivery": str(uuid4()),
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": signature,
    }
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            accepted = await client.post("/webhooks/github", content=body, headers=headers)
            duplicate = await client.post("/webhooks/github", content=body, headers=headers)
            invalid = await client.post(
                "/webhooks/github",
                content=body,
                headers={
                    **headers,
                    "X-GitHub-Delivery": str(uuid4()),
                    "X-Hub-Signature-256": "sha256=00",
                },
            )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert accepted.status_code == 202
    assert accepted.json()["status"] == "accepted"
    assert duplicate.status_code == 202
    assert duplicate.json()["status"] == "duplicate"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_webhook_signature"
