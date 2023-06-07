from . import asyncio
from . import aiohttp


async def get_user_id_data(session: aiohttp.ClientSession, username: str) -> dict:
    """
    Gets the user's data from their username.

    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        username (str): The username of the user.

    Returns:
        dict: User data

    """
    url = "https://users.roblox.com/v1/usernames/users"
    data = {"usernames": [username]}

    async with session.post(url, json=data) as response:
        resp = await response.json()

    return resp


async def get_user_headshot_url_data(session: aiohttp.ClientSession, user_id: str) -> dict:
    """
    Gets the user's headshot data from their ID.

    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        user_id (int): The ID of the user.

    Returns:
        dict: User headshot URL data

    """
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=48x48&format=Png"

    async with session.get(url) as response:
        resp = await response.json()

    return resp


async def convert_tokens(session: aiohttp.ClientSession, token_data: dict[dict]) -> dict[set]:
    """
    Converts a list of player tokens to a list of headshots.

    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        token_data (dict): Dictionary of game instances.

    Returns:
        dict[set]: Dictionary of game instances with headshots.

    """
    url = "https://thumbnails.roblox.com/v1/batch"

    headshots = {}

    # generate payloads
    tasks = []
    temp_task = []

    # limited to 100 tokens per request
    for server in token_data:
        for player_token in token_data[server]["playerTokens"]:
            temp_payload = {
                "requestId": server,
                "token": player_token,
                "type": "AvatarHeadshot",
                "size": "48x48"
            }
            temp_task.append(temp_payload)
            if len(temp_task) == 100:
                tasks.append(session.post(url, json=temp_task))
                temp_task = []

    # send requests
    responses = await asyncio.gather(*tasks)

    # parse responses
    for resp in responses:
        resp = await resp.json()

        if "errors" in resp:
            print(resp)
            continue

        for server in resp["data"]:
            server_id = server["requestId"]
            headshot_id = server["imageUrl"].split("/")[3]
            if server_id not in headshots:
                headshots[server_id] = {headshot_id}

            else:
                headshots[server_id].add(headshot_id)

    return headshots
