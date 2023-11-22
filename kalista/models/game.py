import asyncio
from datetime import datetime, timedelta
from typing import Optional, Coroutine, List

import aiohttp
import pandas as pd
from loguru import logger
from pandas import json_normalize, DataFrame
from pydantic import BaseModel, ConfigDict

from kalista.models.exceptions import InvalidGame

# from kalista.models.league import League
from kalista.models.team import Team

# from kalista.models.tournament import Tournament
# from kalista.models.match import Match

logger.disable("kalista")


class Game(BaseModel):
    """
    Game model
    """

    id: int
    """ A unique integer identifier for the game. """

    match_id: Optional[int] = None
    """ A unique integer identifier for the match. """

    game_number: Optional[int] = None
    """ The game number in a best of series. """

    tournament: Optional[int] = None
    """ A unique integer identifier for the tournament. """

    blue_team: Optional[Team] = None
    """ An instance of :class:`Team` representing the team on the blue side. """

    red_team: Optional[Team] = None
    """ An instance of :class:`Team` representing the team on the red side. """

    winner: Optional[Team] = None
    """ An instance of :class:`Team` representing the winning team. """

    date: Optional[datetime] = None
    """ The date and time of the game. """

    region: Optional[int] = None
    """ A unique integer identifier for the league. """

    league: Optional[str] = None
    """ The unique slug of the league. """

    vod: Optional[str] = None

    patch: Optional[str] = None
    """ The patch version of the game. """

    participants: Optional[DataFrame] = None
    """ A DataFrame containing information about the participants in the game. """

    _header: dict[str] = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    _player_frames: Optional[DataFrame] = pd.DataFrame()
    _team_frames: Optional[DataFrame] = pd.DataFrame()
    _funcs: Optional[List[Coroutine]] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def player_frames(self) -> DataFrame:
        """
        Returns the player frames

        Returns
        -------
        DataFrame
            Player frames, gives information for each frame of a game

        Raises
        ------
        AttributeError
            If frames have not been fetched yet. call await fetch() first.
        """
        if self._player_frames.empty:
            raise AttributeError(
                "Frames have not been fetched yet. call await fetch() first."
            )
        return self._player_frames

    async def fetch(self):
        """
        Fetch all the frame data
        """
        await self.game_data()
        results = await asyncio.gather(*self._funcs)
        self._player_frames = pd.concat([res[1] for res in results], ignore_index=True)
        self._team_frames = pd.concat([res[2] for res in results], ignore_index=True)

    async def game_data(self):
        """
        Gets game data for a given gameID
        """
        logger.info(f"Calculating number of 10s periods in game {self.id}")
        # Calculates the number of 10s periods for the duration of the game
        metadata, participants, first_frames = await self._get_window()
        self.participants = participants
        timestamp = first_frames["timestamp"].min().to_pydatetime()
        timestamp = round_time(timestamp)

        temp_max_ts = timestamp + timedelta(days=1)
        temp_max_ts = temp_max_ts.strftime("%Y-%m-%dT%H:%M:%SZ")

        logger.info(f"Check if game {self.id} has ended")

        _, _, last_frames = await self._get_window(temp_max_ts)

        if not last_frames["gameState"].str.contains("finished").any():
            return

        max_ts = last_frames["timestamp"].max().to_pydatetime()
        max_ts = round_time(max_ts)

        num_periods = round((max_ts - timestamp).total_seconds() / 10)
        logger.info(f"Number of 10s periods: {num_periods}")

        logger.info(f"Calculating game {self.id} data")
        self._funcs = [
            self._get_window(
                (timestamp + timedelta(seconds=i * 10)).strftime("%Y-%m-%dT%H:%M:%SZ")
            )
            for i in range(num_periods)
        ]
        results = []

        return results

    async def _get_window(self, timestamp="") -> tuple[DataFrame]:
        """
        Gets 10s of game data for a given gameID starting at a given timestamp

        Parameters
        ----------
        timestamp
            Timestamp to get frame data for a given gameID, must be increments of 10s.
            Defaults to "". "" gives the first 10s of the game.


        Returns
        -------
        tuple[DataFrame]
            Tuple of DataFrames containing metadata, participants, and teams

        Raises
        ------
        InvalidGame
            If the gameID is invalid
        """

        # Makes request with given params
        if timestamp == "":
            params = {}
        else:
            params = {"startingTime": timestamp}
        try:
            # logger.debug(f"Getting game data for game {self.id} | {timestamp}")
            async with aiohttp.ClientSession() as client:
                try:
                    response = await client.get(
                        f"https://feed.lolesports.com/livestats/v1/window/{self.id}",
                        params=params,
                    )
                    response.raise_for_status()
                except Exception as request_error:
                    logger.error(f"Error getting game {self.id} data: {request_error}")
                    raise InvalidGame(self.id, request_error) from request_error

                raw_data = await response.json()
                if self.match_id is None:
                    self.match_id = raw_data.get("esportsMatchId")
                    self.blue_team = raw_data["gameMetadata"]["blueTeamMetadata"][
                        "esportsTeamId"
                    ]
                    self.red_team = raw_data["gameMetadata"]["redTeamMetadata"][
                        "esportsTeamId"
                    ]
                    self.patch = raw_data["gameMetadata"]["patchVersion"]

                # Blue team metadata to a DataFrame
                blue_metadata = json_normalize(
                    raw_data["gameMetadata"]["blueTeamMetadata"]["participantMetadata"]
                )

                # Red team metadata to a DataFrame
                red_metadata = json_normalize(
                    raw_data["gameMetadata"]["redTeamMetadata"]["participantMetadata"]
                )

                # Combines two metadata frames into 1
                metadata = pd.concat([blue_metadata, red_metadata], ignore_index=True)

                # Splits column into team code and summoner name
                metadata[["code", "summoner_name"]] = metadata[
                    "summonerName"
                ].str.split(expand=True, n=1)

                # Teams
                # Puts json data into DataFrames
                red_team = json_normalize(
                    raw_data["frames"],
                    meta=["redTeam", "rfc460Timestamp", "gameState"],
                )
                blue_team = json_normalize(
                    raw_data["frames"],
                    meta=["blueTeam", "rfc460Timestamp", "gameState"],
                )

                # Drop irrelevant columns, players, and other team
                red_team.drop(
                    list(red_team.filter(regex="participants|blueTeam")),
                    axis=1,
                    inplace=True,
                )
                blue_team.drop(
                    list(blue_team.filter(regex="participants|redTeam")),
                    axis=1,
                    inplace=True,
                )

                # Standardize column names
                red_team.columns = red_team.columns.str.replace(
                    r"redTeam.", "", regex=True
                )
                blue_team.columns = blue_team.columns.str.replace(
                    r"blueTeam.", "", regex=True
                )

                # Insert static data
                red_team["team_id"] = self.red_team
                red_team["side"] = "red"
                red_team["code"] = metadata.code.unique()[0]

                blue_team["team_id"] = self.blue_team
                blue_team["side"] = "blue"
                blue_team["code"] = metadata.code.unique()[1]

                # Combine DataFrames
                teams = pd.concat([red_team, blue_team], ignore_index=True)

                # Convert timestamp from string to datetime
                teams["timestamp"] = pd.to_datetime(
                    teams["rfc460Timestamp"], format="ISO8601"
                ).dt.tz_convert(None)
                teams["game_id"] = self.id

                # Participants
                # Combine participant json data into DataFrame
                blue_participants = json_normalize(
                    raw_data["frames"],
                    ["blueTeam", "participants"],
                    ["rfc460Timestamp"],
                )
                red_participants = json_normalize(
                    raw_data["frames"],
                    ["redTeam", "participants"],
                    ["rfc460Timestamp"],
                )
                participants = pd.concat(
                    [blue_participants, red_participants], ignore_index=True
                )

                # Merge with metadata
                participants = pd.merge(participants, metadata, on="participantId")

                # Convert timestamp from string to datetime
                participants["timestamp"] = pd.to_datetime(
                    participants["rfc460Timestamp"], format="ISO8601"
                ).dt.tz_convert(None)

                participants["game_id"] = self.id

                # Drop useless column
                participants.drop("summonerName", axis=1, inplace=True)

                return metadata, participants, teams
        except Exception as request_error:
            logger.error(f"Error getting game {self.id} data: {request_error}")
            raise InvalidGame(self.id, request_error) from request_error

    async def _get_event_details(self):
        """
        Gets event details for a given gameID
        """
        # TODO: Implement this
        raise NotImplementedError

    def __str__(self):
        return f"{self.blue_team} vs {self.red_team} | {self.patch} | {self.id}"


def round_time(
    dt: datetime = datetime.utcnow(),
    date_delta: timedelta = timedelta(seconds=10),
    round_up: bool = False,
):
    """Round a datetime object to a multiple of a timedelta

    Args:
        dt (datetime): datetime.datetime object, default now.
        date_delta (timedelta) : timedelta object, we round to a multiple of this, default 1 minute.
        round_up (bool) : Round up, down or to nearest
    """
    round_to = date_delta.total_seconds()

    seconds = (dt - dt.min).seconds

    if round_up:
        # // is a floor division, not a comment on following line (like in javascript):
        rounding = (seconds + round_to) // round_to * round_to
    else:
        rounding = seconds // round_to * round_to

    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


class VOD:
    """
    VOD model
    """

    parameter: str = None
    provider: str = None
    locale: str = None
    language_english: str = None
    language_original: str = None

    @property
    def url(self) -> str:
        """
        Returns the url for the VOD
        """
        if self.provider == "youtube":
            return f"https://www.youtu.be/{self.parameter}"
        return ""


if __name__ == "__main__":
    game = Game(id=108206581964974058)
    asyncio.run(game.fetch())

    print(game.player_frames)
