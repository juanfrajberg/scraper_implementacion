import sqlite3
from pathlib import Path

from .config import DATA_DIR


DATABASE_FILE = DATA_DIR / "twitter.db"


def connect() -> sqlite3.Connection:

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_tables() -> None:

    with connect() as db:

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                display_name TEXT
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                author_id TEXT,
                created_at TEXT,
                text TEXT,

                like_count INTEGER,
                retweet_count INTEGER,
                reply_count INTEGER,
                quote_count INTEGER,
                view_count INTEGER,

                conversation_id TEXT,
                parent_tweet_id TEXT,

                url TEXT,
                search_query TEXT,

                FOREIGN KEY (
                    author_id
                )
                REFERENCES users(user_id)
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source_id TEXT,
                target_id TEXT,

                relationship_type TEXT,

                tweet_id TEXT,

                UNIQUE (
                    source_id,
                    target_id,
                    relationship_type,
                    tweet_id
                )
            )
            """
        )

        db.commit()