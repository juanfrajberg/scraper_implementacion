import asyncio

from src.client import create_client
from src.collector import collect_tweets
from src.config import (
    DATE_FROM,
    DATE_TO,
    MAX_TWEETS_PER_SEARCH,
    SEARCHES,
)


async def main():
    print("Iniciando cliente...")

    api = create_client()

    total_tweets = 0

    for search in SEARCHES:
        query = f"{search} since:{DATE_FROM} until:{DATE_TO}"

        print()
        print("=" * 60)
        print(f'Consulta: "{query}"')
        print("=" * 60)

        count = await collect_tweets(
            api=api,
            query=query,
            limit=MAX_TWEETS_PER_SEARCH,
        )

        total_tweets += count

        print(f"Tweets encontrados en esta consulta: {count}")

    print()
    print("=" * 60)
    print(f"Proceso terminado. Tweets encontrados en total: {total_tweets}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
