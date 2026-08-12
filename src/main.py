import asyncio
import json

from .client import create_client
from .collector import tweet_to_data
from .config import (
    RAW_DIR,
    SEARCHES,
    DATE_FROM,
    DATE_TO,
    MAX_TWEETS_PER_SEARCH,
)
from .database import create_tables
from .process import process_tweets


async def collect() -> None:

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = create_client()

    output_file = (
        RAW_DIR / "tweets.jsonl"
    )

    seen_ids: set[str] = set()

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        for search in SEARCHES:

            query = (
                f"{search} "
                f"since:{DATE_FROM} "
                f"until:{DATE_TO}"
            )

            print()
            print(
                f"Buscando: {query}"
            )

            results = await client.search_tweet(
                query,
                "Latest",
                count=20,
            )

            collected = 0

            while results:

                for tweet in results:

                    tweet_id = str(
                        tweet.id
                    )

                    if tweet_id in seen_ids:
                        continue

                    seen_ids.add(tweet_id)

                    data = tweet_to_data(
                        tweet,
                        search,
                    )

                    file.write(
                        json.dumps(
                            data.to_dict(),
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                    collected += 1

                    print(
                        f"[{collected}] "
                        f"@{data.author_username}: "
                        f"{data.text[:80]}"
                    )

                    if (
                        collected
                        >= MAX_TWEETS_PER_SEARCH
                    ):
                        break

                if (
                    collected
                    >= MAX_TWEETS_PER_SEARCH
                ):
                    break

                try:
                    results = (
                        await results.next()
                    )

                except Exception as error:

                    print(
                        f"Error de paginación: "
                        f"{error}"
                    )

                    break

    print()
    print(
        f"Tweets únicos: "
        f"{len(seen_ids)}"
    )


async def main() -> None:

    create_tables()

    await collect()

    process_tweets()

    print()
    print("Proyecto finalizado.")


if __name__ == "__main__":
    asyncio.run(main())