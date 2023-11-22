from __future__ import annotations

from datetime import datetime
from typing import Optional, List

import aiohttp
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from kalista.models.exceptions import InvalidLeague, InvalidTournament
from kalista.models.tournament import Tournament

logger.disable("kalista")


class League(BaseModel):
    """
    League Model
    """

    league_id: Optional[int] = Field(
        None, alias="id", description="The unique ID of the league"
    )
    """ The unique ID of the league """

    slug: str = Field(None, description="The slug of the league")
    """ The slug of the league. A slug is a unique string identifier for a league."""

    name: str = Field(None, description="The name of the league")
    """ The name of the league. """

    image: str = Field(None, description="The image URL of the league logo")
    """ The image URL of the league logo."""

    region: str = Field(None, description="The region of the league")
    """ The region of the league. """

    _tournament_list: list[Tournament] = PrivateAttr(default=[])
    """ The list of tournaments for this league. List of :class:`Tournament` objects."""

    _header: dict[str, str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _get_leagues_params: dict[str, str] = {"hl": "en-US"}
    _get_leagues_url: str = "https://esports-api.lolesports.com/persisted/gw/getLeagues"
    _get_tournament_params = {"hl": "en-US", "leagueId": league_id}
    _get_tournament_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getTournamentsForLeague"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def fetch(self) -> None:
        """
        Fetch the league data
        """
        try:
            await self._get_league()
            await self._get_tournaments()
        except Exception as e:
            raise InvalidLeague(self.slug, e) from e

    async def _get_league(self) -> None:
        """
        Get the league data

        Returns
        -------

        """
        ids: list[int] = []
        logger.info(f"Getting league {self.slug} data")
        async with aiohttp.ClientSession(headers=self._header) as client:
            try:
                response = await client.get(
                    self._get_leagues_url, params=self._get_leagues_params
                )
                response.raise_for_status()

            except Exception as request_error:
                logger.error(f"Error getting league {self.slug} data: {request_error}")
                raise InvalidLeague(self.slug, request_error) from request_error

            data = await response.json()
            try:
                leagues: dict = data["data"]["leagues"]
            except Exception as data_error:
                logger.error(f"Error getting league {self.slug} data: {data_error}")
                raise InvalidLeague(self.slug, data_error) from data_error

            for league in leagues:
                ids.append(int(league["id"]))
                if league["slug"] == self.slug:
                    self.league_id = int(league["id"])
                    self.name = league["name"]
                    self.image = league["image"]
                    self.region = league["region"]

            if self.league_id is None or self.league_id not in ids:
                raise InvalidLeague(self.slug, None)
            logger.success(f"Got league {self.slug} data")

    async def _get_tournaments(self):
        logger.info(f"Getting tournaments for league {self.slug}")
        async with aiohttp.ClientSession(headers=self._header) as client:
            try:
                get_tournament_params = {"hl": "en-US", "leagueId": self.league_id}

                response = await client.get(
                    self._get_tournament_url, params=get_tournament_params
                )
                response.raise_for_status()
            except Exception as request_error:
                logger.error(
                    f"Error getting tournaments for league {self.slug}: {request_error}"
                )
                raise InvalidTournament(
                    self.slug, None, request_error
                ) from request_error

            data = await response.json()

            # Rename columns
            tournaments = [
                {
                    "id": t["id"],
                    "slug": t["slug"],
                    "league_slug": self.slug,
                    "region": self.region,
                    "start_date": datetime.fromisoformat(t["startDate"]),
                    "end_date": datetime.fromisoformat(t["endDate"]),
                }
                for t in data["data"]["leagues"][0]["tournaments"]
            ]
            self._tournament_list = [Tournament(**t) for t in tournaments]

    @property
    def tournaments(self) -> List[Tournament]:
        """
        Get the tournaments for this league

        Returns
        -------
        List[Tournament]
            The list of tournaments for this league

        Raises
        ------
        AttributeError
            If the tournaments have not been fetched yet
        """

        if self._tournament_list is None:
            raise AttributeError(
                "Tournaments have not been fetched yet. call await fetch() first."
            )
        return self._tournament_list

    def __str__(self) -> str:
        if self.slug is None:
            raise AttributeError("League slug is not provided")
        return str(self.slug)

    @classmethod
    async def get_all_leagues(cls) -> list[League]:
        """
        Get all the leagues
        Returns
        -------
        list[League]
            The list of all League of Legends leagues

        """
        leagues = []
        logger.debug(cls.__private_attributes__)
        async with aiohttp.ClientSession(
            headers=cls.__private_attributes__["_header"].default
        ) as client:
            try:
                response = await client.get(
                    url=cls.__private_attributes__["_get_leagues_url"].default,
                    params=cls.__private_attributes__["_get_leagues_params"].default,
                )
                response.raise_for_status()

            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting leagues: {client_error}")

            data = await response.json()
            logger.success("Got leagues")
            for league in data["data"]["leagues"]:
                leagues.append(
                    League(
                        id=int(league["id"]),
                        slug=league["slug"],
                        name=league["name"],
                        image=league["image"],
                        region=league["region"],
                    )
                )
        return leagues
