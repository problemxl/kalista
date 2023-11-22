import pytest

from kalista.models.league import League
from kalista.models.schedule import Schedule


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "once",
    }


@pytest.fixture(scope="module")
@pytest.mark.vcr
def league():
    """
    Basic test fixture for League class
    """
    return League(slug="lcs")


@pytest.fixture(scope="module")
@pytest.mark.vcr
def schedule():
    """
    Basic test fixture for Schedule class
    """
    return Schedule(id=98767991299243165)


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_schedule(schedule):
    """
    Basic tests for Schedule class
    """
    assert len(schedule.matches) == 0
    await schedule.fetch()
    assert len(schedule.matches) > 0
