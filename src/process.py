import json

from .config import RAW_DIR
from .database import connect


def process_tweets() -> None:

    input_file = (
        RAW_DIR / "tweets.jsonl"
    )

    if not input_file.exists():

        raise FileNotFoundError(
            f"No existe {input_file}"
        )

    with connect() as db:

        with input_file.open(
            encoding="utf-8"
        ) as file:

            for line in file:

                tweet = json.loads(line)

                author_id = (
                    tweet["author_id"]
                )

                if author_id:

                    db.execute(
                        """
                        INSERT OR IGNORE INTO users
                        (
                            user_id,
                            username,
                            display_name
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            author_id,
                            tweet[
                                "author_username"
                            ],
                            tweet[
                                "author_name"
                            ],
                        ),
                    )

                db.execute(
                    """
                    INSERT OR IGNORE INTO tweets
                    (
                        tweet_id,
                        author_id,
                        created_at,
                        text,

                        like_count,
                        retweet_count,
                        reply_count,
                        quote_count,
                        view_count,

                        conversation_id,
                        parent_tweet_id,

                        url,
                        search_query
                    )
                    VALUES (
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?,
                        ?, ?
                    )
                    """,
                    (
                        tweet["tweet_id"],
                        author_id,
                        tweet["created_at"],
                        tweet["text"],

                        tweet["like_count"],
                        tweet["retweet_count"],
                        tweet["reply_count"],
                        tweet["quote_count"],
                        tweet["view_count"],

                        tweet["conversation_id"],
                        tweet["parent_tweet_id"],

                        tweet["url"],
                        tweet["search_query"],
                    ),
                )

        db.commit()

    print("Datos procesados correctamente.")