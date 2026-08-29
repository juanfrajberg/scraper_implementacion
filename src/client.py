from twscrape import API


DB_PATH = "data/accounts.db"


def create_client() -> API:
    return API(DB_PATH)
