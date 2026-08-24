import hashlib
import hmac
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.errors import ApiError
from autodev_api.models import GitHubWebhookDelivery

SUPPORTED_EVENTS = {
    "check_run",
    "check_suite",
    "installation",
    "installation_repositories",
    "issue_comment",
    "issues",
    "ping",
    "pull_request",
    "push",
    "workflow_run",
}


def verify_signature(body: bytes, signature: str | None, secret: str) -> None:
    if signature is None or not signature.startswith("sha256="):
        raise ApiError(401, "invalid_webhook_signature", "The webhook signature is invalid.")
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ApiError(401, "invalid_webhook_signature", "The webhook signature is invalid.")


def parse_payload(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ApiError(400, "invalid_webhook_payload", "The webhook payload is invalid.") from error
    if not isinstance(value, dict):
        raise ApiError(400, "invalid_webhook_payload", "The webhook payload must be an object.")
    return value


def nested_external_id(payload: dict[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if not isinstance(value, dict):
        return None
    external_id = value.get("id")
    return (
        external_id if isinstance(external_id, int) and not isinstance(external_id, bool) else None
    )


async def persist_delivery(
    session: AsyncSession,
    *,
    delivery_id: str,
    event_type: str,
    body: bytes,
    payload: dict[str, Any],
) -> bool:
    existing = await session.scalar(
        select(GitHubWebhookDelivery.id).where(GitHubWebhookDelivery.delivery_id == delivery_id)
    )
    if existing is not None:
        return False
    action = payload.get("action")
    delivery = GitHubWebhookDelivery(
        delivery_id=delivery_id,
        event_type=event_type,
        action=action if isinstance(action, str) else None,
        installation_external_id=nested_external_id(payload, "installation"),
        repository_external_id=nested_external_id(payload, "repository"),
        payload_sha256=hashlib.sha256(body).hexdigest(),
        payload=payload,
        status="ignored" if event_type == "ping" else "pending",
    )
    try:
        async with session.begin_nested():
            session.add(delivery)
            await session.flush()
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return False
    return True
