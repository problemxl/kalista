from datetime import datetime
from typing import Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel

from kalista.models.exceptions import InvalidTournament
from kalista.models.game import Game
from kalista.models.team import Team


class Tournament(BaseModel):
    """
    Tournament Model
    """

    id: Optional[int] = None
    """ The unique ID of the tournament. """

    slug: Optional[str] = ""
    """ The slug of the tournament. A slug is a unique string identifier for a tournament. """

    start_date: Optional[datetime] = None
    """ The start date of the tournament. """

    end_date: Optional[datetime] = None
    """ The end date of the tournament. """

    league_id: Optional[int] = None
    """ The unique ID of the league. """

    league_slug: Optional[str] = None
    """ The league slug of the tournament. """

    teams: Optional[list[Team]] = None
    """ The list of teams in the tournament. List of :class:`Team` objects. """

    region: Optional[str] = ""
    """ The region of the tournament."""

    games: Optional[list[Game]] = []
    """ The list of games in the tournament. List of :class:`Game` objects. """

    _header: dict[str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _get_tournaments_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getTournamentsForLeague"
    )
    _get_tournaments_params: dict[str, str] = {"hl": "en-US", "leagueId": None}

    async def fetch(self):
        """
        Fetch all the tournament data
        """
        await self._get_data()

    async def _get_data(self):
        """
        Get the games for this tournament
        """
        raise NotImplementedError

    def __str__(self):
        return self.slug

    @property
    def is_active(self) -> bool:
        """
        Check if the tournament is active

        Returns
        -------
        bool
            True if the tournament is active, False otherwise
        """
        return self.start_date < datetime.utcnow() < self.end_date

    @property
    def name(self) -> str:
        """
        Get the name of the tournament

        Returns
        -------
        str
            The name of the tournament
        """

        name = self.slug.split("_")
        final_name = ""
        for word in name:
            if word == self.league_slug or len(word) < 3:
                final_name += word.upper()
            else:
                final_name += word.capitalize()

            final_name += " "
        return final_name

    @classmethod
    async def get_tournaments_for_league(cls, league_id: str) -> list["Tournament"]:
        """
        Get a tournament by its slug
        """
        async with aiohttp.ClientSession(headers=cls._header) as client:
            try:
                response = await client.get(
                    cls._get_tournaments_url, params=cls._get_tournaments_params
                )
                response.raise_for_status()
            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting tournaments: {client_error}")
                raise InvalidTournament(
                    league_id, tournament_id=None, exception=client_error
                ) from client_error
            data = response.json()
            tournaments = data["data"]["leagues"][0]["tournaments"]
            return [
                cls(
                    id=tournament["id"],
                    slug=tournament["slug"],
                    start_date=datetime.fromisoformat(tournament["startDate"]),
                    end_date=datetime.fromisoformat(tournament["endDate"]),
                    league_id=league_id,
                )
                for tournament in tournaments
            ]
