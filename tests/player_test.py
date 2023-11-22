import pytest


from kalista.models.player import Player
from kalista.models.team import Team


@pytest.fixture(scope="module")
@pytest.mark.asyncio
@pytest.mark.vcr
async def player() -> Player:
    team = Team(slug="clg")
    await team.fetch()
    return team.roster[0]


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_players_team():
    pass


def test_get_players_league():
    pass
