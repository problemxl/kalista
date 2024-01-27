import pytest

from kalista.models.league import League, InvalidLeague


@pytest.fixture(scope="module")
@pytest.mark.vcr
def league():
    return League(slug="lcs")


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_league(league):
    """
    Basic tests for League class
    """
    await league.fetch()
    assert isinstance(league, League)
    assert league.name == "LCS"
    assert league.league_id == 98767991299243165
    assert league.region == "NORTH AMERICA"
    assert len(league.tournaments) > 0


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_invalid_slug():
    with pytest.raises(InvalidLeague):
        league = League(slug="invalid")
        await league.fetch()


@pytest.mark.asyncio
# @pytest.mark.vcr
async def test_get_leagues():
    leagues = await League.get_all_leagues()
    assert len(leagues) > 0
    assert isinstance(leagues[0], League)
