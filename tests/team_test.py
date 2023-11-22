import pytest

from kalista.models.team import Team


@pytest.fixture(scope="module")
@pytest.mark.vcr
def team():
    return Team(slug="clg")


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_team(team):
    # await team.get_team()
    await team.fetch()
    assert isinstance(team, Team)
    assert team.name == "CLG"
    assert team.code == "CLG"
    assert team.id == 98926509884398584
    assert team.region == "NORTH AMERICA"
    assert len(team.roster) > 0


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_teams():
    """
    Tests for get all teams
    """
    teams = await Team.get_all_teams()
    assert len(teams) > 0
    assert isinstance(teams[0], Team)
