from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.auth import Principal, get_principal
from autodev_api.config import Settings, get_settings
from autodev_api.database import get_session
from autodev_api.errors import ApiError
from autodev_api.github_webhooks import (
    SUPPORTED_EVENTS,
    parse_payload,
    persist_delivery,
    verify_signature,
)
from autodev_api.schemas import (
    ActivityPage,
    AuditEventRead,
    GitHubWebhookAccepted,
    ProjectCreate,
    ProjectPage,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
)
from autodev_api.services import (
    cancel_task,
    create_project,
    create_task,
    get_project,
    get_task,
    list_activity,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/v1")
webhook_router = APIRouter()
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


@webhook_router.post(
    "/webhooks/github",
    response_model=GitHubWebhookAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["webhooks"],
)
async def github_webhook_endpoint(
    request: Request,
    session: SessionDependency,
    settings: SettingsDependency,
    delivery_id: Annotated[str, Header(alias="X-GitHub-Delivery", min_length=1, max_length=64)],
    event_type: Annotated[str, Header(alias="X-GitHub-Event", min_length=1, max_length=64)],
    signature: Annotated[str | None, Header(alias="X-Hub-Signature-256")] = None,
) -> GitHubWebhookAccepted:
    if not settings.github_integration_enabled or settings.github_webhook_secret is None:
        raise ApiError(503, "github_integration_disabled", "GitHub integration is disabled.")
    chunks: list[bytes] = []
    body_size = 0
    async for chunk in request.stream():
        body_size += len(chunk)
        if body_size > settings.github_webhook_max_body_bytes:
            raise ApiError(413, "webhook_payload_too_large", "The webhook payload is too large.")
        chunks.append(chunk)
    body = b"".join(chunks)
    verify_signature(body, signature, settings.github_webhook_secret.get_secret_value())
    if event_type not in SUPPORTED_EVENTS:
        return GitHubWebhookAccepted(status="ignored", delivery_id=delivery_id)
    payload = parse_payload(body)
    created = await persist_delivery(
        session,
        delivery_id=delivery_id,
        event_type=event_type,
        body=body,
        payload=payload,
    )
    return GitHubWebhookAccepted(
        status="accepted" if created else "duplicate",
        delivery_id=delivery_id,
    )


@router.post(
    "/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    tags=["projects"],
)
async def create_project_endpoint(
    payload: ProjectCreate,
    response: Response,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> ProjectRead:
    project, created = await create_project(session, principal, payload)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return ProjectRead.model_validate(project)


@router.get("/projects", response_model=ProjectPage, tags=["projects"])
async def list_projects_endpoint(
    session: SessionDependency,
    principal: PrincipalDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    cursor: str | None = None,
) -> ProjectPage:
    projects, next_cursor = await list_projects(session, principal, limit=limit, cursor=cursor)
    return ProjectPage(
        items=[ProjectRead.model_validate(project) for project in projects],
        next_cursor=next_cursor,
    )


@router.get("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
async def get_project_endpoint(
    project_id: UUID,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> ProjectRead:
    return ProjectRead.model_validate(await get_project(session, principal, project_id))


@router.patch("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
async def update_project_endpoint(
    project_id: UUID,
    payload: ProjectUpdate,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> ProjectRead:
    project = await update_project(session, principal, project_id, payload)
    return ProjectRead.model_validate(project)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
async def create_task_endpoint(
    project_id: UUID,
    payload: TaskCreate,
    response: Response,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> TaskRead:
    task, created = await create_task(session, principal, project_id, payload)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return TaskRead.model_validate(task)


@router.get("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
async def get_task_endpoint(
    task_id: UUID,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> TaskRead:
    return TaskRead.model_validate(await get_task(session, principal, task_id))


@router.post("/tasks/{task_id}/cancel", response_model=TaskRead, tags=["tasks"])
async def cancel_task_endpoint(
    task_id: UUID,
    session: SessionDependency,
    principal: PrincipalDependency,
) -> TaskRead:
    return TaskRead.model_validate(await cancel_task(session, principal, task_id))


@router.get(
    "/projects/{project_id}/activity",
    response_model=ActivityPage,
    tags=["activity"],
)
async def list_activity_endpoint(
    project_id: UUID,
    session: SessionDependency,
    principal: PrincipalDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: str | None = None,
) -> ActivityPage:
    events, next_cursor = await list_activity(
        session,
        principal,
        project_id,
        limit=limit,
        cursor=cursor,
    )
    return ActivityPage(
        items=[AuditEventRead.model_validate(event) for event in events],
        next_cursor=next_cursor,
    )
