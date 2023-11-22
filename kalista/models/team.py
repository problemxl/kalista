from typing import Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel

from kalista.models.player import Player

logger.disable("kalista")


class Team(BaseModel):
    """
    Team Model
    """

    id: Optional[int] = None
    """ The unique ID of the team. """

    name: Optional[str] = None
    """ The name of the team. """

    slug: str = None
    """ The slug of the team. A slug is a unique string identifier for a team. """

    code: Optional[str] = None
    """ The code of the team. """

    image: Optional[str] = None
    """ The image URL of the team logo. """

    region: Optional[str] = None
    """ The region of the team. """

    league_name: Optional[str] = None
    """ The league name of the team. """

    roster: Optional[list[Player]] = None
    """ The list of players in the team. List of :class:`Player` objects. """

    alternative_image: Optional[str] = None
    """ The alternative image URL of the team logo."""

    background_image: Optional[str] = None
    """ The background image URL of the team logo. """

    _header: dict[str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _get_team_params: dict[str, str] = {"hl": "en-US", "id": slug}
    _get_team_url: str = "https://esports-api.lolesports.com/persisted/gw/getTeams"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._get_team_params["id"] = self.slug
        if len(kwargs) == 10:
            return

    def __str__(self):
        return self.name

    async def fetch(self):
        """
        Fetch all the team data
        """
        await self._get_team()

    async def _get_team(self):
        async with aiohttp.ClientSession(headers=self._header) as client:
            try:
                response = await client.get(
                    self._get_team_url, params=self._get_team_params
                )
                response.raise_for_status()

            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting team {self.name} data: {client_error}")
            data = await response.json()
            team = data["data"]["teams"][0]
            if team["slug"] == self.slug:
                self.id = int(team["id"])
                self.slug = team["slug"]
                self.name = team["name"]
                self.code = team["code"]
                self.image = team["image"]
                self.alternative_image = team["alternativeImage"]
                self.background_image = team["backgroundImage"]
                self.region = team["homeLeague"]["region"]
                self.league_name = team["homeLeague"]["name"]
                self.roster = [
                    Player(
                        id=player["id"],
                        summoner_name=player["summonerName"],
                        first_name=player["firstName"],
                        last_name=player["lastName"],
                        image=player["image"],
                        role=player["role"],
                        team_id=self.id,
                        team_name=self.name,
                    )
                    for player in team["players"]
                ]
                # logger.debug(f"{self.name}: {team['players']}")

            # logger.success(f"Got team {self.name} data")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    @classmethod
    async def get_all_teams(cls) -> list["Team"]:
        """
        Get all the teams

        Returns
        -------
        list[Team]
            The list of all teams
        """
        teams = []
        async with aiohttp.ClientSession(
            headers=cls.__private_attributes__["_header"].default
        ) as client:
            try:
                response = await client.get(
                    url=cls.__private_attributes__["_get_team_url"].default,
                    params={"hl": "en-US"},
                )
                response.raise_for_status()

            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting teams: {client_error}")

            data = await response.json()
            for team in data["data"]["teams"]:
                if team["slug"] == "tbd":
                    continue
                try:
                    home_league = team.get("homeLeague", {})
                    if home_league is None:
                        home_league = {}

                    teams.append(
                        cls(
                            id=int(team["id"]),
                            slug=team["slug"],
                            name=team["name"],
                            code=team["code"],
                            image=team["image"],
                            alternative_image=team["alternativeImage"],
                            background_image=team["backgroundImage"],
                            region=home_league.get("region"),
                            league_name=home_league.get("name"),
                        )
                    )
                except Exception as e:
                    logger.error(f"Error getting team {team['name']}: {e} | {team}")
                    raise e
        return teams
