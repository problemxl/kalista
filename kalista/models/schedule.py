from typing import Optional

import aiohttp
import arrow
from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel

from kalista.models.exceptions import InvalidSchedule
from kalista.models.match import Match

logger.disable("kalista")


class Schedule(BaseModel):
    """
    Schedule model
    """

    league_id: Optional[int] = None
    """ The unique ID of the league. """

    matches: Optional[list[Match]] = []
    """ The list of matches in the schedule. List of :class:`Match` objects."""

    _header: dict[str, str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _get_schedule_params: dict[str, str | int] = {"hl": "en-US"}
    _get_schedule_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getSchedule"
    )
    _get_tournament_params = {"hl": "en-US", "leagueId": id}
    _get_tournament_url: str = (
        "https://esports-api.lolesports.com/persisted/gw/getTournamentsForLeague"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.league_id:
            self._get_schedule_params["leagueId"] = self.league_id

    async def fetch(self):
        """
        Fetch all the schedule data
        """
        # await self._get_tournament()
        await self._get_schedule()

    async def _get_schedule(self, client: ClientSession = None) -> None:
        page_token = ""
        page_token_queue = []
        page_token_fetched = set()
        client_flag = False
        if client is None:
            client = ClientSession(headers=self._header)
            client_flag = True
        while page_token != None:
            page_tokens = await self._fetch_data(client)
            page_token_queue.extend(page_tokens)
            page_token_fetched.add(page_token)
            logger.info(f"Got page {page_token}")
            page_token = page_token_queue.pop(0)
            while page_token in page_token_fetched:
                page_token = page_token_queue.pop(0)

            self._get_schedule_params["pageToken"] = page_token

        if client_flag:
            await client.close()

    async def _fetch_data(self, client: ClientSession) -> list[str]:
        try:
            response = await client.get(
                self._get_schedule_url, params=self._get_schedule_params
            )
            response.raise_for_status()

        except Exception as request_error:
            logger.error(f"Error getting schedule data: {request_error}")
            raise InvalidSchedule(
                self.league_id, request_error
            ) from request_error
        data = await response.json()
        # logger.success("Got schedule data")
        page_tokens = [data["data"]["schedule"]["pages"]["older"], data["data"]["schedule"]["pages"]["newer"]]
        matches = data["data"]["schedule"]["events"][::-1]
        for match in matches:
            if match.get("match") is None:
                continue
            match_id = match["match"]["id"]
            date = arrow.get(match["startTime"]).datetime
            team1 = match["match"]["teams"][0]["code"]
            team2 = match["match"]["teams"][1]["code"]
            league = match["league"]["name"]
            best_of = match["match"]["strategy"]["count"]
            match = Match(
                id=match_id,
                start_time=date,
                team1_code=team1,
                team2_code=team2,
                league=league,
                best_of=best_of,
            )
            self.matches.append(match)
        return page_tokens

    async def _get_tournament(self):
        """

        """
        async with aiohttp.ClientSession(headers=self._header) as client:
            try:
                response = await client.get(
                    self._get_tournament_url, params=self._get_tournament_params
                )
                response.raise_for_status()

            except aiohttp.ClientError as client_error:
                logger.error(f"Error getting tournament data: {client_error}")

            data = await response.json()
            for tournament in data["data"]["tournaments"]:
                if tournament["id"] == self.tournament_id:
                    self.league_id = tournament["leagueId"]
                    break

    async def _get_games(self):
        pass

    @property
    def start_date(self):
        """
        Get the start date of the tournament
        """
        return self._start_date

    def __str__(self) -> str:
        """
        Get the string representation of the schedule

        Returns
        -------
        str
            The string representation of the schedule
        """
        result = ""
        for match in self.matches:
            result += f"{match}\n"

        return result
