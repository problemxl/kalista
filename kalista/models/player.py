from typing import Optional

from pydantic import BaseModel


# from kalista.models.league import League
# from kalista.models.team import Team
# from kalista.models.tournament import Tournament


class Player(BaseModel):
    """
    Player Model
    """

    id: Optional[int] = None
    """ The unique ID of the player. """

    first_name: Optional[str] = None
    """ The first name of the player. """

    last_name: Optional[str] = None
    """ The last name of the player. """

    summoner_name: Optional[str] = ""
    """ The summoner name of the player. """

    image: Optional[str] = None
    """ The image URL of the player. """

    role: Optional[str] = None
    """ The role of the player. """

    status: Optional[str] = None
    """ The status of the player. """

    team: Optional[str] = None
    """ The team of the player. """

    team_id: Optional[int] = None
    """ The team id. """

    team_name: Optional[str] = None
    """ The team name. """

    region: Optional[str] = None
    """ The region of the player. """

    league: Optional[str] = None
    """ The league of the player. """

    tournaments: Optional[list[int]] = []
    games: Optional[list[int]] = []

    def __str__(self):
        return self.summoner_name

    def _tournaments(self):
        # TODO: Implement this
        raise NotImplementedError
        # return self.tournaments

    def _games(self):
        # TODO: Implement this
        raise NotImplementedError
        # return self.games
