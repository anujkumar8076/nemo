from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, desc, or_, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from autodev_api.github_client import GitHubRepository
from autodev_api.models import (
    GitHubInstallation,
    GitHubInstallationRepository,
    GitHubInstallationStatus,
)
from autodev_api.services import decode_cursor, encode_cursor


class GitHubInstallationUnavailableError(Exception):
    """The requested installation is not an active member of the tenant."""


@dataclass(frozen=True, slots=True)
class RepositorySyncResult:
    available: int
    removed: int
    synchronized_at: datetime


async def list_installations(
    session: AsyncSession,
    *,
    organization_id: UUID,
    limit: int,
    cursor: str | None,
) -> tuple[list[GitHubInstallation], str | None]:
    query = select(GitHubInstallation).where(GitHubInstallation.organization_id == organization_id)
    if cursor is not None:
        created_at, record_id = decode_cursor(cursor)
        query = query.where(
            or_(
                GitHubInstallation.created_at < created_at,
                and_(
                    GitHubInstallation.created_at == created_at,
                    GitHubInstallation.id < record_id,
                ),
            )
        )
    records = list(
        (
            await session.scalars(
                query.order_by(
                    desc(GitHubInstallation.created_at), desc(GitHubInstallation.id)
                ).limit(limit + 1)
            )
        ).all()
    )
    has_more = len(records) > limit
    items = records[:limit]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if has_more else None
    return items, next_cursor


async def list_repositories(
    session: AsyncSession,
    *,
    organization_id: UUID,
    installation_id: UUID | None,
    include_removed: bool,
    limit: int,
    cursor: str | None,
) -> tuple[list[GitHubInstallationRepository], str | None]:
    query = select(GitHubInstallationRepository).where(
        GitHubInstallationRepository.organization_id == organization_id
    )
    if installation_id is not None:
        query = query.where(GitHubInstallationRepository.installation_id == installation_id)
    if not include_removed:
        query = query.where(GitHubInstallationRepository.available.is_(True))
    if cursor is not None:
        created_at, record_id = decode_cursor(cursor)
        query = query.where(
            or_(
                GitHubInstallationRepository.created_at < created_at,
                and_(
                    GitHubInstallationRepository.created_at == created_at,
                    GitHubInstallationRepository.id < record_id,
                ),
            )
        )
    records = list(
        (
            await session.scalars(
                query.order_by(
                    desc(GitHubInstallationRepository.created_at),
                    desc(GitHubInstallationRepository.id),
                ).limit(limit + 1)
            )
        ).all()
    )
    has_more = len(records) > limit
    items = records[:limit]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if has_more else None
    return items, next_cursor


async def synchronize_installation_repositories(
    session: AsyncSession,
    *,
    organization_id: UUID,
    installation_id: UUID,
    repositories: list[GitHubRepository],
    synchronized_at: datetime | None = None,
) -> RepositorySyncResult:
    """Atomically reconcile one tenant-owned GitHub installation inventory."""
    sync_time = (synchronized_at or datetime.now(UTC)).astimezone(UTC)
    external_ids = [repository.id for repository in repositories]
    if len(external_ids) != len(set(external_ids)):
        raise ValueError("repository inventory contains duplicate external IDs")

    installation = await session.scalar(
        select(GitHubInstallation)
        .where(
            GitHubInstallation.id == installation_id,
            GitHubInstallation.organization_id == organization_id,
            GitHubInstallation.status == GitHubInstallationStatus.ACTIVE,
        )
        .with_for_update()
    )
    if installation is None:
        raise GitHubInstallationUnavailableError(
            "GitHub installation is unavailable for this organization"
        )

    if repositories:
        values = [
            {
                "organization_id": organization_id,
                "installation_id": installation_id,
                "external_id": repository.id,
                "node_id": repository.node_id,
                "owner": repository.owner.login,
                "name": repository.name,
                "full_name": repository.full_name,
                "private": repository.private,
                "default_branch": repository.default_branch,
                "html_url": repository.html_url,
                "archived": repository.archived,
                "disabled": repository.disabled,
                "available": True,
                "last_seen_at": sync_time,
                "removed_at": None,
            }
            for repository in repositories
        ]
        statement = insert(GitHubInstallationRepository).values(values)
        excluded = statement.excluded
        await session.execute(
            statement.on_conflict_do_update(
                index_elements=["installation_id", "external_id"],
                set_={
                    "organization_id": excluded.organization_id,
                    "node_id": excluded.node_id,
                    "owner": excluded.owner,
                    "name": excluded.name,
                    "full_name": excluded.full_name,
                    "private": excluded.private,
                    "default_branch": excluded.default_branch,
                    "html_url": excluded.html_url,
                    "archived": excluded.archived,
                    "disabled": excluded.disabled,
                    "available": True,
                    "last_seen_at": sync_time,
                    "removed_at": None,
                    "updated_at": sync_time,
                },
            )
        )

    removal_filter = [
        GitHubInstallationRepository.organization_id == organization_id,
        GitHubInstallationRepository.installation_id == installation_id,
        GitHubInstallationRepository.available.is_(True),
    ]
    if external_ids:
        removal_filter.append(GitHubInstallationRepository.external_id.not_in(external_ids))
    removal = await session.execute(
        update(GitHubInstallationRepository)
        .where(*removal_filter)
        .values(available=False, removed_at=sync_time, updated_at=sync_time)
    )
    installation.last_synced_at = sync_time
    await session.commit()
    return RepositorySyncResult(
        available=len(repositories),
        removed=removal.rowcount or 0,
        synchronized_at=sync_time,
    )
