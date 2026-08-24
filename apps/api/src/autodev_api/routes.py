from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.auth import Principal, get_principal
from autodev_api.database import get_session
from autodev_api.schemas import (
    ActivityPage,
    AuditEventRead,
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
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


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
