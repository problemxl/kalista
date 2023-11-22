import pytest

from kalista.models.game import Game


@pytest.fixture(scope="module")
@pytest.mark.vcr
def game() -> Game:
    """
    Pytest fixture to get a game object for testing

    Returns
    -------
    Game
        The game object
    """
    return Game(id=108206581964974058)


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_get_game(game: Game):
    """
    Test if the game object is fetched correctly

    Parameters
    ----------
    game
        The game object
    """
    assert isinstance(game, Game)
    # check if game.frames raises error
    with pytest.raises(AttributeError) as e:
        _ = game.player_frames
        assert "Frames have not been fetched yet. call await fetch() first." in str(
            e.value
        )
    await game.fetch()
    assert len(game.player_frames) > 0
