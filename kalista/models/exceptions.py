"""
This module contains all the exceptions that can be raised by the models.
"""


class KalistaException(Exception):
    """Base exception class for Kalista."""

    @property
    def message(self):
        """Returns the exception message."""
        raise NotImplementedError


class InvalidLeague(KalistaException):
    """Raised when the league slug is invalid."""

    def __init__(self, slug: str, exception: Exception):
        self.slug: str = slug
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid league slug: {self.slug}"


class InvalidTeam(KalistaException):
    """Raised when the team slug is invalid."""

    def __init__(self, slug: str, exception: Exception):
        self.slug: str = slug
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid team slug: {self.slug}"


class InvalidPlayer(KalistaException):
    """Raised when the player slug is invalid."""

    def __init__(self, summoner_name: str, exception: Exception):
        self.summoner_name: str = summoner_name
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid Player: {self.summoner_name}"


class InvalidMatch(KalistaException):
    """Raised when the match id is invalid."""

    def __init__(self, match_id: int, exception: Exception):
        self.match_id: int = match_id
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid Match: {self.match_id}"


class InvalidTournament(KalistaException):
    """Raised when the tournament id is invalid."""

    def __init__(
        self,
        league_slug: str = None,
        tournament_id: int | None = None,
        exception: Exception = None,
    ):
        self.league_slug = league_slug
        self.tournament_id: int = tournament_id
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid Tournament: {self.tournament_id}"


class InvalidSchedule(KalistaException):
    """Raised when the schedule id is invalid."""

    def __init__(self, league_id: int, exception: Exception):
        self.league_id: int = league_id
        self.exception: Exception = exception

    @property
    def message(self):
        return f"Invalid Schedule: {self.league_id}"


class InvalidGame(KalistaException):
    """Raised when the game id is invalid."""

    def __init__(self, game_id: int, exception: Exception):
        self.game_id: int = game_id
        self.exception: Exception = exception

    @property
    def message(self) -> str:
        return f"Invalid Game: {self.game_id}"


class InvalidStandings(KalistaException):
    """Raised when the standings id is invalid."""

    def __init__(self, tournament_id: int, exception: Exception):
        self.tournament_id: int = tournament_id
        self.exception: Exception = exception

    @property
    def message(self) -> str:
        return f"Invalid Standings: {self.tournament_id}"
