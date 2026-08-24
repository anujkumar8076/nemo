from datetime import timedelta
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from autodev_api.github_claims import begin_installation_claim, state_digest


def test_claim_state_digest_is_stable_and_not_reversible() -> None:
    raw_state = "one-time-state-with-sufficient-entropy-for-this-test"
    digest = state_digest(raw_state)

    assert digest == state_digest(raw_state)
    assert len(digest) == 64
    assert raw_state not in digest


@pytest.mark.parametrize("lifetime", [timedelta(0), timedelta(minutes=31)])
@pytest.mark.asyncio
async def test_claim_lifetime_bounds_are_enforced_before_database_use(
    lifetime: timedelta,
) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        await begin_installation_claim(
            cast(AsyncSession, None),
            organization_id=uuid4(),
            user_id=uuid4(),
            lifetime=lifetime,
        )
