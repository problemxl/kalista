==========
Quickstart
==========


Code Examples
=============

Import
------

First lets import the library

.. code-block:: python

    from kalista.models import *



.. note::
    When retrieving data from the API, you will need to use the `fetch` method. This method will initialize the object with
    the data from the API. Lets take a look at an example of how to fetch the LCK league.

League
------

.. code-block:: python

    async def league_example():
        """
        League example
        """
        # Create a league object
        league = League(slug="lck")

        # Fetch the league data
        await league.fetch()

        # Print the league name
        print(league.name)


Schedule
--------

Now lets get the schedule for the League of Legends World Championship. You can get the league id by fetching the
league data using.

.. code-block:: python

    League.get_all_leagues()

But for this example we will just use the id, `98767975604431411`

.. code-block:: python

    async def schedule_example():
        """
        Schedule example
        """
        worlds_schedule = Schedule(league_id="98767975604431411")

        # Fetch the schedule data
        await worlds_schedule.fetch()

        print(worlds_schedule)


Standings
---------

Now lets get the standings for LCK Summer 2023.

.. code-block:: python

    async def standings_example():
        """
        Standings example
        """
        lck_standings = Standings(tournament_id="110371551277508787")

        # Fetch the standings data
        await lck_standings.fetch()

        print(lck_standings)

Game
----

Now lets get the game data for the first game of the 2023 World Championship Grand Finals.

The Game model contains a lot of data. `player_frames` and `team_frames` contain the data for each server tick of the game.
The `player_frames` contain the data for each player in the game, and the `team_frames` contain the data for each team in the game.

.. code-block:: python

    async def game_example():
        """
        Game example
        """

        game = Game(id="110853020184706766")

        # Fetch the game data
        await game.fetch()

        player_frames = game.player_frames
        team_frames = game.team_frames


