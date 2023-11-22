from typing import Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel

from kalista.models.exceptions import InvalidStandings
from kalista.models.team import Team

logger.disable("kalista")


class Standings(BaseModel):
    """
    Standings Model
    """

    region: Optional[str] = None
    """ The region of the standings. """

    league_id: Optional[int] = None
    """ The unique ID of the league. """

    tournament_id: Optional[int] = None
    """ The unique ID of the tournament. """

    teams: Optional[list[Team]] = []
    """ The list of teams in the standings. List of :class:`Team` objects."""

    week: Optional[int] = None
    """ The week of the standings. """

    standings: dict[int, str | list[str]] = {}
    """ The standings. """

    _header: dict[str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _get_standings_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getStandings"
    )
    _get_standings_params: dict[str, str | int] = {
        "hl": "en-US",
        "tournamentId": tournament_id,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._get_standings_params["tournamentId"] = self.tournament_id
        logger.info(self._get_standings_params)

    async def fetch(self):
        """
        Fetch all the standings data
        """
        await self._get_standings()

    async def _get_standings(self):
        """
        Get standings from API
        """
        async with aiohttp.ClientSession(headers=self._header) as client:
            try:
                response = await client.get(
                    self._get_standings_url, params=self._get_standings_params
                )
                response.raise_for_status()
            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting standings: {client_error}")
                raise InvalidStandings(
                    self.tournament_id, client_error
                ) from client_error
            data = await response.json()
            stages = data["data"]["standings"][0]["stages"]

            for stage in stages:
                if stage["name"] == "Regular Season":
                    standings = stage

            teams_set = set()
            for teams in standings["sections"][0]["rankings"]:
                ordinal = int(teams["ordinal"])
                self.standings[ordinal] = []
                for team in teams["teams"]:
                    self.standings[ordinal].append(team["code"])
                    teams_set.add(team["code"])
            self.teams = list(teams_set)


def convert_to_ordinal(n: int):
    """
    Return the ordinal suffix of a number
    """
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix
