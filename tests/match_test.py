import pytest

from kalista.models.match import Match


@pytest.fixture(scope="module")
@pytest.mark.vcr
def match():
    return Match(id=108998961199895792)


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_match(match):
    assert isinstance(match, Match)

    with pytest.raises(AttributeError) as e:
        _ = match.games
    assert "Games have not been fetched yet. call await fetch() first." in str(e.value)

    await match.fetch()
    assert len(match.games) > 0


@pytest.mark.asyncio
# @pytest.mark.vcr
async def test_specific_match():
    match = Match(id=111720485044707008)
    await match.fetch()
    assert len(match.games) > 0
