import time

import asyncio
import aiohttp

from rosearch.game_utils import *
from rosearch.user_utils import *


class RoSearchResult:
    fields = ["game_id", "id", "player_count", "max_players", "ping", "fps"]

    def __init__(self, data: dict):
        self.data = data

        self.fps = None
        self.ping = None
        self.max_players = None
        self.player_count = None
        self.game_id = None
        self.id = None

        for field in self.fields:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f"<RoSearchResult id={self.id} game_id={self.game_id} player_count={self.player_count} max_players={self.max_players} ping={self.ping} fps={self.fps}>"

    def to_join_cmd(self) -> str:
        """Converts the result to a console join command.

        Returns:
            str: The console join command.

        """
        if "error" in self.data:
            return self.data["error"]

        return f"Roblox.GameLauncher.joinGameInstance({self.game_id}, \"{self.id}\")"


class RoSearcher:
    def __init__(self, rbx_cookie: str):
        self.headers: dict = {".ROBLOSECURITY": rbx_cookie}
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    def __enter__(self):
        self.loop.run_until_complete(self._start())
        return self

    async def _start(self):
        self.session = aiohttp.ClientSession(headers=self.headers)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.run_until_complete(self._stop())

    async def _stop(self):
        await self.session.close()

    def search(self, username: str | int, game_id: str | int) -> RoSearchResult:
        """
        Searches for a user in specific game.

        Args:
            username (str|int): The username or ID of the user.
            game_id (str|int): The ID of the game.

        Returns:
            dict: Game instance data

        """
        user_data = self.loop.run_until_complete(self._get_user_info(username))

        if "error" in user_data:
            return RoSearchResult(user_data)

        print(f"user_id: {user_data['id']}\nheadshot_id: {user_data['headshot_id']}")

        # search game servers
        game_instances = self.loop.run_until_complete(self._search_game_servers(game_id))

        if "error" in game_instances:
            return RoSearchResult(game_instances)

        # parse game servers
        found_game_instance = self.loop.run_until_complete(self._parse_game_servers(game_instances, user_data))

        if "error" not in found_game_instance:
            print("-" * 50)
            print("Found user in game instance:")
            for data_point in found_game_instance:
                print(f"{data_point}: {found_game_instance[data_point]}")
            print("-" * 50)

            found_game_instance["game_id"] = game_id

        return RoSearchResult(found_game_instance)

    async def _search_game_servers(self, game_id: str) -> dict:
        """Extracts all game instances of a game.

        Args:
            game_id (str): The ID of the game.

        Returns:
            dict: The game instances of the game.

        """

        t1 = time.perf_counter()
        game_servers = await get_game_instances(self.session, game_id)
        t2 = time.perf_counter()

        if "error" in game_servers:
            return game_servers

        print(f"Finished getting game servers in {t2 - t1:.2f} seconds.")

        # reformat data
        game_server_dict = {game_server["id"]: game_server for game_server in game_servers}

        return game_server_dict

    async def _parse_game_servers(self, game_servers: dict, user_data: dict) -> dict:
        """
        Parses through the game servers to find the user.

        Args:
            game_servers (dict): The game servers to parse through.
            user_data (dict): The user data.

        Returns:
            dict: The game server the user is in.

        """

        # convert game instance data to headshot data
        headshot_data = await convert_tokens(self.session, game_servers)

        for server in headshot_data:
            if user_data["headshot_id"] in headshot_data[server]:
                return game_servers[server]

        return {"error": "User not found."}

    async def _get_user_info(self, username: str) -> dict:
        """
        Gets the user's ID from their username.

        Args:
            username (str): The username of the user.

        Returns:
            dict: A dictionary containing the user id and headshot id.

        """

        if not username.isnumeric():
            # attempt to get user id from username
            user_data = await get_user_id_data(self.session, username)
            if len(user_data["data"]) == 0:
                return {"error": "Invalid username."}

            user_id = user_data["data"][0]["id"]

        else:
            user_id = username

        user_id = str(user_id)

        headshot_response = await get_user_headshot_url_data(self.session, user_id)

        if "errors" in headshot_response or len(headshot_response["data"]) == 0:
            return {"error": "Invalid user ID."}

        image_url = headshot_response["data"][0]["imageUrl"]

        # extract id
        headshot_id = image_url.split("/")[3]

        return {"id": user_id, "headshot_id": headshot_id}
