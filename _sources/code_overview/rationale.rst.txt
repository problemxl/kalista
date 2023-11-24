How Kalista Works
=================

First and foremost, Kalista is an API Wrapper. It is designed to make it easy to interact with the undocumented Riot
Games eSports API. It does this by providing a simple interface to the API, and by handling all of the HTTP requests
and responses.

Kalista is built on top of the `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_ library, which is an asynchronous
HTTP client/server library. This means that Kalista is able to make multiple requests at the same time. This makes Kalista
very fast.

For example, if you wanted the game data for a game, the API requires you to make a request for each 10 second interval
of the game. This means that a 30 minute game would require 180 requests. I found that it took about 2 minutes for a
synchronous program to get the data. Kalista can do it in about 10 seconds.

Kalista uses the Pydantic library to define the data model for the API. This library provides many useful features,
including:

- Data validation
- Data conversion
- Data serialization.




