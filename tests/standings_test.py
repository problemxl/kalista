import pytest

from kalista.models.standings import Standings


@pytest.fixture(scope="module")
@pytest.mark.vcr
def standings():
    return Standings(tournament_id=108206581962155974)


@pytest.fixture(scope="module")
@pytest.mark.vcr
def current_standings():
    return Standings(tournament_id=109517090066605615)


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_standings(standings):
    await standings.fetch()
    assert isinstance(standings, Standings)
    assert standings.tournament_id == 108206581962155974
    assert len(standings.standings) > 0


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_standing_order(standings):
    await standings.fetch()
    assert standings.standings.get(1) == ["EG"]
    assert standings.standings.get(2) == ["100"]
    assert standings.standings.get(3) == ["TL"]
    assert standings.standings.get(4) == ["CLG"]
    assert standings.standings.get(5) == ["C9"]
    assert standings.standings.get(6) == ["FLY"]
    assert standings.standings.get(7) == ["TSM"]
    assert standings.standings.get(8) == ["GG"]
    assert standings.standings.get(9) == ["IMT"]
    assert standings.standings.get(10) == ["DIG"]


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_current_standings(current_standings):
    await current_standings.fetch()
    assert isinstance(current_standings, Standings)
    # assert current_standings.tournament_id == 109517090066605615
    # assert len(current_standings.standings) > 0
