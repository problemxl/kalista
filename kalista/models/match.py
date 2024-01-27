from datetime import datetime
from typing import Optional

from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel

from kalista.models.exceptions import InvalidMatch
from kalista.models.game import Game
from kalista.models.team import Team


# logger.disable("kalista")


class Match(BaseModel):
    """
    Match model
    """

    id: int
    """ The unique ID of the match. """

    tournament_id: Optional[int] = None
    """ The unique ID of the tournament. """

    league_slug: Optional[str] = None
    """ The slug of the league. A slug is a unique string identifier for a league."""

    team1: Optional[Team] = None
    """ The first :class:Team in the match. """

    team1_code: Optional[str] = None
    """ The code of the first :class:Team in the match. """

    team2: Optional[Team] = None
    """ The second :class:Team in the match. """

    team2_code: Optional[str] = None
    """ The code of the second :class:Team in the match. """

    winner: Optional[str] = None
    """ The winner of the match. """

    start_time: Optional[datetime] = None
    """ The date of the match. """

    region: Optional[str] = None
    """ The region of the match. """

    league_id: Optional[int] = None
    """ The unique ID of the league. """

    is_live: Optional[bool] = None
    """ Whether the match is live or not. """

    _games: Optional[list[Game]] = None
    """ The list of games in the match. List of :class:`Game` objects."""

    best_of: Optional[int] = None
    """ The number of games in the match. """

    _get_event_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getEventDetails"
    )

    _get_event_params: dict[str, str | int] = {"hl": "en-US"}

    _header: dict[str, str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._get_event_params["id"] = self.id

    @property
    def games(self) -> list[Game]:
        """
        Get the games for this match

        Returns
        -------
        list[Game]
            The list of games in the match. List of :class:`Game` objects.

        Raises
        ------
        AttributeError
            If the games have not been fetched yet. Call await fetch() first.
        """
        if self._games is None:
            raise AttributeError(
                "Games have not been fetched yet. call await fetch() first."
            )
        return self._games

    async def fetch(self, client: ClientSession = None) -> None:
        """
        Fetch all the match data
        """
        await self._get_data(client)

    async def _get_data(self, client: ClientSession = None) -> None:
        """
        Get the match data

        :type client: aiohttp client session
        :param client: The aiohttp client session
        :return:
        """

        if client is None:
            async with ClientSession(headers=self._header) as client:
                await self._fetch_data(client)
        else:
            await self._fetch_data(client)

    async def _fetch_data(self, client):
        try:
            response = await client.get(
                self._get_event_url, params=self._get_event_params, headers=self._header
            )
            response.raise_for_status()

        except Exception as request_error:
            logger.error(f"Error getting match {self.id} data: {request_error}")
            raise InvalidMatch(self.id, request_error) from request_error
        data = await response.json()
        logger.success(f"Got match {self.id} data")
        try:
            event = data["data"]["event"]
            match = event.get("match")
        except Exception as data_error:
            logger.error(f"Error getting match {self.id} data: {data_error}")
            raise InvalidMatch(self.id, data_error) from data_error
        self.tournament_id = event.get("tournament").get("id")
        self.league_slug = event.get("league").get("slug")
        self.best_of = match.get("strategy").get("count")
        team1 = match.get("teams")[0]
        team2 = match.get("teams")[1]
        self.team1 = Team(
            id=team1.get("id"),
            name=team1.get("name"),
            code=team1.get("code"),
            image=team1.get("image"),
        )
        self.team2 = Team(
            id=team2.get("id"),
            name=team2.get("name"),
            code=team2.get("code"),
            image=team2.get("image"),
        )
        # try:
        if team1.get("result") is not None:
            self.winner = self.team1 if team1.get("result").get("gameWins") > team2.get("result").get(
                "gameWins") else self.team2
        else:
            self.winner = None

        self._games = []
        games = match.get("games")
        for game in games:
            teams = game.get("teams")
            if teams:
                if teams[0].get("side") == "blue":
                    if teams[0].get("id") == self.team1.id:
                        blue_team = self.team1
                        red_team = self.team2
                    else:
                        blue_team = self.team2
                        red_team = self.team1
                else:
                    if teams[0].get("id") == self.team1.id:
                        blue_team = self.team2
                        red_team = self.team1
                    else:
                        blue_team = self.team1
                        red_team = self.team2
            else:
                blue_team = team1
                red_team = team2
            game = Game(
                id=game.get("id"),
                match_id=self.id,
                tournament_id=self.tournament_id,
                game_number=game.get("number"),
                blue_team=blue_team,
                red_team=red_team,
                region=self.region,
                league=self.league_slug,
            )
            self._games.append(game)

    def __str__(self):
        if self.start_time is None:
            return f"{self.team1_code} vs {self.team2_code}"
        return f"{self.team1_code} vs {self.team2_code} - {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
