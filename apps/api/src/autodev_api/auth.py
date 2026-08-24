from dataclasses import dataclass
from hmac import compare_digest
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.config import Settings, get_settings
from autodev_api.database import get_session
from autodev_api.errors import ApiError
from autodev_api.models import Membership


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: UUID
    organization_id: UUID


async def get_principal(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    scheme, separator, token = (authorization or "").partition(" ")
    expected_token = settings.bootstrap_api_token.get_secret_value()
    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not token
        or not compare_digest(token, expected_token)
    ):
        raise ApiError(
            401,
            "authentication_required",
            "A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    membership = await session.scalar(
        select(Membership.id).where(
            Membership.user_id == settings.bootstrap_user_id,
            Membership.organization_id == settings.bootstrap_organization_id,
        )
    )
    if membership is None:
        raise ApiError(
            403,
            "membership_required",
            "The authenticated user is not a member of the configured organization.",
        )
    return Principal(
        user_id=settings.bootstrap_user_id,
        organization_id=settings.bootstrap_organization_id,
    )
