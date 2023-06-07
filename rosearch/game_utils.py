from . import aiohttp


async def get_game_instances(session: aiohttp.ClientSession, game_id: str | int, cursor: str = None) -> dict:
    """
    Gets the game instances from a game id.

    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        game_id (str): The ID of the game.
        cursor (str, optional): The cursor of the game instances page. Defaults to None.

    Returns:
        dict: A dictionary containing the game instances.
    """
    url = f"https://games.roblox.com/v1/games/{game_id}/servers/0"
    params = {
        "sortOrder": 2,
        "excludeFullGames": "false",
        "limit": 100,
    }

    if cursor:
        params["cursor"] = cursor

    async with session.get(url, params=params) as response:
        resp = await response.json()
        if "errors" in resp:
            return {"error": "Invalid game ID."}

        data = resp["data"]
        next_cursor = resp["nextPageCursor"]
        if next_cursor:
            next_data = await get_game_instances(session, game_id, next_cursor)
            data += next_data

    return data



