import base64
import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.auth import Principal
from autodev_api.errors import ApiError
from autodev_api.models import AuditEvent, Project, ProjectStatus, Task, TaskStatus
from autodev_api.schemas import ProjectCreate, ProjectUpdate, TaskCreate

TERMINAL_TASK_STATUSES = {
    TaskStatus.COMPLETED,
    TaskStatus.FAILED,
    TaskStatus.CANCELLED,
}


def encode_cursor(created_at: datetime, record_id: UUID) -> str:
    payload = json.dumps(
        {"created_at": created_at.astimezone(UTC).isoformat(), "id": str(record_id)},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
        created_at = datetime.fromisoformat(payload["created_at"])
        record_id = UUID(payload["id"])
        if created_at.tzinfo is None:
            raise ValueError("cursor timestamp must include a timezone")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ApiError(400, "invalid_cursor", "The pagination cursor is invalid.") from error
    return created_at, record_id


def add_audit_event(
    session: AsyncSession,
    *,
    principal: Principal,
    project_id: UUID,
    event_type: str,
    entity_type: str,
    entity_id: UUID,
    task_id: UUID | None = None,
    details: dict[str, object] | None = None,
) -> None:
    session.add(
        AuditEvent(
            organization_id=principal.organization_id,
            project_id=project_id,
            task_id=task_id,
            actor_user_id=principal.user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
        )
    )


def project_payload_matches(project: Project, payload: ProjectCreate) -> bool:
    return (
        project.name == payload.name
        and project.slug == payload.slug
        and project.description == payload.description
    )


async def create_project(
    session: AsyncSession, principal: Principal, payload: ProjectCreate
) -> tuple[Project, bool]:
    existing = await session.scalar(
        select(Project).where(
            Project.organization_id == principal.organization_id,
            Project.client_request_id == payload.client_request_id,
        )
    )
    if existing is not None:
        if not project_payload_matches(existing, payload):
            raise ApiError(
                409,
                "idempotency_conflict",
                "The client request ID was already used with a different project payload.",
            )
        return existing, False

    slug_owner = await session.scalar(
        select(Project.id).where(
            Project.organization_id == principal.organization_id,
            Project.slug == payload.slug,
        )
    )
    if slug_owner is not None:
        raise ApiError(409, "project_slug_conflict", "A project with this slug already exists.")

    project = Project(
        organization_id=principal.organization_id,
        client_request_id=payload.client_request_id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        created_by_user_id=principal.user_id,
    )
    try:
        async with session.begin_nested():
            session.add(project)
            await session.flush()
            add_audit_event(
                session,
                principal=principal,
                project_id=project.id,
                event_type="project.created",
                entity_type="project",
                entity_id=project.id,
                details={"name": project.name, "slug": project.slug},
            )
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise ApiError(
            409,
            "project_conflict",
            "The project conflicts with an existing record.",
        ) from error
    await session.refresh(project)
    return project, True


async def get_project(session: AsyncSession, principal: Principal, project_id: UUID) -> Project:
    project = await session.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == principal.organization_id,
        )
    )
    if project is None:
        raise ApiError(404, "project_not_found", "The project was not found.")
    return project


async def list_projects(
    session: AsyncSession,
    principal: Principal,
    *,
    limit: int,
    cursor: str | None,
) -> tuple[list[Project], str | None]:
    query = select(Project).where(Project.organization_id == principal.organization_id)
    if cursor is not None:
        created_at, record_id = decode_cursor(cursor)
        query = query.where(
            or_(
                Project.created_at < created_at,
                and_(Project.created_at == created_at, Project.id < record_id),
            )
        )
    query = query.order_by(desc(Project.created_at), desc(Project.id)).limit(limit + 1)
    projects = list((await session.scalars(query)).all())
    has_more = len(projects) > limit
    items = projects[:limit]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if has_more else None
    return items, next_cursor


async def update_project(
    session: AsyncSession,
    principal: Principal,
    project_id: UUID,
    payload: ProjectUpdate,
) -> Project:
    project = await session.scalar(
        select(Project)
        .where(
            Project.id == project_id,
            Project.organization_id == principal.organization_id,
        )
        .with_for_update()
    )
    if project is None:
        raise ApiError(404, "project_not_found", "The project was not found.")
    if project.version != payload.expected_version:
        raise ApiError(
            409,
            "version_conflict",
            "The project changed after it was read.",
            details={"current_version": project.version},
        )

    changed_fields: list[str] = []
    for field in ("name", "description", "status"):
        if field not in payload.model_fields_set:
            continue
        value = getattr(payload, field)
        if field == "status" and value is not None:
            value = ProjectStatus(value)
        if getattr(project, field) != value:
            setattr(project, field, value)
            changed_fields.append(field)
    if changed_fields:
        project.version += 1
        add_audit_event(
            session,
            principal=principal,
            project_id=project.id,
            event_type="project.updated",
            entity_type="project",
            entity_id=project.id,
            details={"changed_fields": changed_fields, "version": project.version},
        )
    await session.commit()
    await session.refresh(project)
    return project


def task_payload_matches(task: Task, payload: TaskCreate) -> bool:
    return task.title == payload.title and task.description == payload.description


async def create_task(
    session: AsyncSession,
    principal: Principal,
    project_id: UUID,
    payload: TaskCreate,
) -> tuple[Task, bool]:
    project = await get_project(session, principal, project_id)
    if project.status != ProjectStatus.ACTIVE:
        raise ApiError(409, "project_archived", "Tasks cannot be created for an archived project.")

    existing = await session.scalar(
        select(Task).where(
            Task.organization_id == principal.organization_id,
            Task.client_request_id == payload.client_request_id,
        )
    )
    if existing is not None:
        if existing.project_id != project_id or not task_payload_matches(existing, payload):
            raise ApiError(
                409,
                "idempotency_conflict",
                "The client request ID was already used with a different task payload.",
            )
        return existing, False

    task = Task(
        organization_id=principal.organization_id,
        project_id=project_id,
        client_request_id=payload.client_request_id,
        title=payload.title,
        description=payload.description,
        created_by_user_id=principal.user_id,
    )
    try:
        async with session.begin_nested():
            session.add(task)
            await session.flush()
            add_audit_event(
                session,
                principal=principal,
                project_id=project_id,
                task_id=task.id,
                event_type="task.created",
                entity_type="task",
                entity_id=task.id,
                details={"title": task.title, "mode": task.mode.value},
            )
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise ApiError(
            409,
            "task_conflict",
            "The task conflicts with an existing record.",
        ) from error
    await session.refresh(task)
    return task, True


async def get_task(session: AsyncSession, principal: Principal, task_id: UUID) -> Task:
    task = await session.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id == principal.organization_id,
        )
    )
    if task is None:
        raise ApiError(404, "task_not_found", "The task was not found.")
    return task


async def cancel_task(session: AsyncSession, principal: Principal, task_id: UUID) -> Task:
    task = await session.scalar(
        select(Task)
        .where(
            Task.id == task_id,
            Task.organization_id == principal.organization_id,
        )
        .with_for_update()
    )
    if task is None:
        raise ApiError(404, "task_not_found", "The task was not found.")
    if task.status == TaskStatus.CANCELLED:
        return task
    if task.status in TERMINAL_TASK_STATUSES:
        raise ApiError(
            409,
            "task_not_cancellable",
            f"A task in status '{task.status.value}' cannot be cancelled.",
        )
    task.status = TaskStatus.CANCELLED
    task.cancelled_at = datetime.now(UTC)
    task.cancelled_by_user_id = principal.user_id
    add_audit_event(
        session,
        principal=principal,
        project_id=task.project_id,
        task_id=task.id,
        event_type="task.cancelled",
        entity_type="task",
        entity_id=task.id,
    )
    await session.commit()
    await session.refresh(task)
    return task


async def list_activity(
    session: AsyncSession,
    principal: Principal,
    project_id: UUID,
    *,
    limit: int,
    cursor: str | None,
) -> tuple[list[AuditEvent], str | None]:
    await get_project(session, principal, project_id)
    query = select(AuditEvent).where(
        AuditEvent.organization_id == principal.organization_id,
        AuditEvent.project_id == project_id,
    )
    if cursor is not None:
        created_at, record_id = decode_cursor(cursor)
        query = query.where(
            or_(
                AuditEvent.created_at < created_at,
                and_(AuditEvent.created_at == created_at, AuditEvent.id < record_id),
            )
        )
    query = query.order_by(desc(AuditEvent.created_at), desc(AuditEvent.id)).limit(limit + 1)
    events = list((await session.scalars(query)).all())
    has_more = len(events) > limit
    items = events[:limit]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if has_more else None
    return items, next_cursor
