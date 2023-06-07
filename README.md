### RoSearch
A Python library for searching for users in a Roblox game
#### Dependencies
- aiohttp
- asyncio

### Usage
Create a RoSearcher object with a Roblox cookie
Use the .search() method to search for a user in a game

```python
# create searcher object using context manager
from rosearch import RoSearcher
with RoSearcher("COOKIE") as searcher:
    search_result = searcher.search("USERNAME", "GAME_ID")
```

Using the .to_join_cmd() method, you can get a browser console command to join the user's game
### Example Usage
```python
import os
from dotenv import load_dotenv

from rosearch import RoSearcher


def main():
    # get Roblox cookie from .env file
    load_dotenv()
    COOKIE = os.getenv("RBLX_COOKIE")

    USERNAME = "USERNAME"
    GAME_ID = "GAME_ID"

    with RoSearcher(COOKIE) as searcher:
        search_result = searcher.search(USERNAME, GAME_ID)
        print(search_result.to_join_cmd())


if __name__ == "__main__":
    main()

```