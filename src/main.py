import asyncio

from src.client import create_client
from src.collector import collect_tweets


QUERY = "Argentina since:2026-07-19 until:2026-07-20"
LIMIT = 20


async def main():
    print("Iniciando cliente...")

    api = create_client()

    count = await collect_tweets(
        api=api,
        query=QUERY,
        limit=LIMIT,
    )

    print()
    print(f"Proceso terminado. Tweets encontrados: {count}")


if __name__ == "__main__":
    asyncio.run(main())
