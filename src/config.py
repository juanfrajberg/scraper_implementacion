from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

COOKIES_FILE = BASE_DIR / "cookies.json"


# ---------------------------------------
# EXPERIMENTO
# ---------------------------------------

DATE_FROM = "2026-07-19"
DATE_TO = "2026-07-20"


SEARCHES = [
    '"Argentina"',
    '"España Argentina"',
    '"Argentina España"',
    '"Argentina campeón"',
]


MAX_TWEETS_PER_SEARCH = 100
