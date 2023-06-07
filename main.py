import os

from dotenv import load_dotenv

from rosearch import RoSearcher


def main():
    load_dotenv()

    USERNAME = "LittleWarden21"
    GAME_ID = "5702593762"

    with RoSearcher(os.getenv("RBLX_COOKIE")) as searcher:
        search_result = searcher.search(USERNAME, GAME_ID)
        print(search_result.to_join_cmd())


if __name__ == "__main__":
    main()
