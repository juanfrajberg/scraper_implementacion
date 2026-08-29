import json
from collections import Counter
from pathlib import Path


THREADS_FILE = Path("data/threads.jsonl")


def load_threads():
    with THREADS_FILE.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def top_threads(threads, limit=10):
    """Conversaciones con más tweets."""

    ranking = sorted(
        threads,
        key=lambda thread: len(thread["tweets"]),
        reverse=True,
    )

    print("=" * 70)
    print("TOP 10 - CONVERSACIONES MÁS GRANDES")
    print("=" * 70)

    for i, thread in enumerate(ranking[:limit], 1):
        print(
            f"{i:2}. tweets={len(thread['tweets']):4} "
            f"| id={thread['conversation_id']}"
        )


def top_root_tweets(threads, limit=10):
    """
    Tweets raíz con mayor cantidad de respuestas
    dentro del hilo recuperado.
    """

    ranking = []

    for thread in threads:
        tweets = thread["tweets"]

        root_id = str(thread["conversation_id"])

        replies = sum(
            1
            for tweet in tweets
            if str(tweet.get("in_reply_to")) == root_id
        )

        root = next(
            (
                tweet
                for tweet in tweets
                if str(tweet["tweet_id"]) == root_id
            ),
            None,
        )

        if root is None:
            continue

        ranking.append((replies, root))

    ranking.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print()
    print("=" * 70)
    print("TOP 10 - TWEETS RAÍZ CON MÁS RESPUESTAS")
    print("=" * 70)

    for i, (replies, tweet) in enumerate(
        ranking[:limit],
        1,
    ):
        print(
            f"{i:2}. respuestas={replies:5} "
            f"| id={tweet['tweet_id']} "
            f"| @{tweet['username']}"
        )
        print(f"    {tweet['text'][:150]}")


def top_participants(threads, limit=10):
    """
    Usuarios que aparecen en más tweets dentro
    de todas las conversaciones.
    """

    counter = Counter()

    for thread in threads:
        for tweet in thread["tweets"]:
            counter[tweet["username"]] += 1

    print()
    print("=" * 70)
    print("TOP 10 - PARTICIPANTES")
    print("=" * 70)

    for i, (username, count) in enumerate(
        counter.most_common(limit),
        1,
    ):
        print(
            f"{i:2}. tweets={count:5} | @{username}"
        )


def orphan_replies(threads, limit=20):
    """
    Tweets que responden a otro tweet que no está
    presente dentro de la conversación recuperada.
    """

    results = []

    for thread in threads:
        tweets = thread["tweets"]

        ids = {
            str(tweet["tweet_id"])
            for tweet in tweets
        }

        for tweet in tweets:
            parent_id = tweet.get("in_reply_to")

            if (
                parent_id is not None
                and str(parent_id) not in ids
            ):
                results.append(
                    (thread["conversation_id"], tweet)
                )

    print()
    print("=" * 70)
    print("RESPUESTAS SIN TWEET PADRE RECUPERADO")
    print("=" * 70)

    print(f"Total: {len(results)}")

    for conversation_id, tweet in results[:limit]:
        print(
            f"id={tweet['tweet_id']} "
            f"| conv={conversation_id} "
            f"| reply_to={tweet['in_reply_to']} "
            f"| @{tweet['username']}"
        )


def conversation_participation(threads, limit=10):
    """
    Muestra para cada una de las conversaciones más grandes
    cuántos tweets aporta cada usuario.
    """

    ranking = sorted(
        threads,
        key=lambda thread: len(thread["tweets"]),
        reverse=True,
    )

    print()
    print("=" * 70)
    print("PARTICIPACIÓN EN LAS CONVERSACIONES MÁS GRANDES")
    print("=" * 70)

    for thread in ranking[:limit]:
        counter = Counter(
            tweet["username"]
            for tweet in thread["tweets"]
        )

        print()
        print(
            f"CONVERSACIÓN "
            f"{thread['conversation_id']} "
            f"({len(thread['tweets'])} tweets)"
        )

        for username, count in counter.most_common(5):
            print(
                f"  @{username}: {count} tweets"
            )


def main():
    threads = load_threads()

    print("=" * 70)
    print("ANÁLISIS DE CONVERSACIONES")
    print("=" * 70)
    print(f"Conversaciones analizadas: {len(threads)}")

    total_tweets = sum(
        len(thread["tweets"])
        for thread in threads
    )

    print(f"Tweets analizados: {total_tweets}")

    top_threads(threads)
    top_root_tweets(threads)
    top_participants(threads)
    orphan_replies(threads)
    conversation_participation(threads)


if __name__ == "__main__":
    main()
