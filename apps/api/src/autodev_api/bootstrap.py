from sqlalchemy import select

from autodev_api.config import Settings
from autodev_api.database import session_factory
from autodev_api.models import Membership, MembershipRole, Organization, User


async def ensure_bootstrap_identity(settings: Settings) -> None:
    async with session_factory.begin() as session:
        user = await session.get(User, settings.bootstrap_user_id)
        if user is None:
            session.add(
                User(
                    id=settings.bootstrap_user_id,
                    email=settings.bootstrap_user_email,
                    display_name=settings.bootstrap_user_name,
                )
            )
        elif user.email != settings.bootstrap_user_email:
            raise RuntimeError("bootstrap user ID already belongs to a different email")

        organization = await session.get(Organization, settings.bootstrap_organization_id)
        if organization is None:
            session.add(
                Organization(
                    id=settings.bootstrap_organization_id,
                    name=settings.bootstrap_organization_name,
                    slug=settings.bootstrap_organization_slug,
                )
            )
        elif organization.slug != settings.bootstrap_organization_slug:
            raise RuntimeError("bootstrap organization ID already belongs to a different slug")

        membership = await session.scalar(
            select(Membership).where(
                Membership.organization_id == settings.bootstrap_organization_id,
                Membership.user_id == settings.bootstrap_user_id,
            )
        )
        if membership is None:
            session.add(
                Membership(
                    organization_id=settings.bootstrap_organization_id,
                    user_id=settings.bootstrap_user_id,
                    role=MembershipRole.OWNER,
                )
            )
