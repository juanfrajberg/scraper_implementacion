import json
from collections import Counter, defaultdict
from contextlib import suppress
from datetime import datetime
from pathlib import Path

THREADS_FILE = Path("data/threads.jsonl")
PROCESSED_FILE = Path("data/processed.jsonl")
USERS_FILE = Path("data/users.jsonl")


def load_jsonl(path):
    """Carga un archivo JSONL."""

    data = []

    if not path.exists():
        return data

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return data


def process_thread(thread):
    """Calcula estadísticas de una conversación."""

    conversation_id = str(thread["conversation_id"])
    tweets = thread.get("tweets", [])

    if not tweets:
        return None

    users = Counter(tweet["username"] for tweet in tweets if tweet.get("username"))

    dates = []

    for tweet in tweets:
        with suppress(KeyError, ValueError):
            dates.append(datetime.fromisoformat(tweet["date"]))

    dates.sort()

    start_date = dates[0].isoformat() if dates else None

    end_date = dates[-1].isoformat() if dates else None

    duration_seconds = 0

    if len(dates) >= 2:
        duration_seconds = (dates[-1] - dates[0]).total_seconds()

    total_likes = sum(tweet.get("likes", 0) or 0 for tweet in tweets)

    total_retweets = sum(tweet.get("retweets", 0) or 0 for tweet in tweets)

    total_replies = sum(tweet.get("replies", 0) or 0 for tweet in tweets)

    total_quotes = sum(tweet.get("quotes", 0) or 0 for tweet in tweets)

    total_views = sum(tweet.get("views", 0) or 0 for tweet in tweets)

    languages = Counter(tweet["lang"] for tweet in tweets if tweet.get("lang"))

    hashtags = Counter()

    for tweet in tweets:
        for hashtag in tweet.get("hashtags", []):
            hashtags[hashtag] += 1

    mentioned_users = Counter()

    for tweet in tweets:
        for username in tweet.get(
            "mentioned_users",
            [],
        ):
            mentioned_users[username] += 1

    root_tweet = next(
        (tweet for tweet in tweets if str(tweet.get("tweet_id")) == conversation_id),
        tweets[0],
    )

    return {
        "conversation_id": conversation_id,
        "tweet_count": len(tweets),
        "participant_count": len(users),
        "participants": [
            {
                "username": username,
                "tweet_count": count,
            }
            for username, count in users.most_common()
        ],
        "root_user": root_tweet.get("username"),
        "root_tweet_id": root_tweet.get("tweet_id"),
        "start_date": start_date,
        "end_date": end_date,
        "duration_seconds": duration_seconds,
        "duration_minutes": round(
            duration_seconds / 60,
            2,
        ),
        "duration_hours": round(
            duration_seconds / 3600,
            2,
        ),
        "total_likes": total_likes,
        "total_retweets": total_retweets,
        "total_replies": total_replies,
        "total_quotes": total_quotes,
        "total_views": total_views,
        "languages": dict(languages),
        "hashtags": dict(hashtags.most_common()),
        "mentioned_users": dict(mentioned_users.most_common()),
    }


def process_users(threads):
    """
    Calcula estadísticas globales por usuario.
    """

    users = defaultdict(
        lambda: {
            "tweet_count": 0,
            "conversation_ids": set(),
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "quotes": 0,
            "views": 0,
            "first_date": None,
            "last_date": None,
        }
    )

    for thread in threads:
        conversation_id = str(thread["conversation_id"])

        for tweet in thread.get("tweets", []):
            username = tweet.get("username")

            if not username:
                continue

            data = users[username]

            data["tweet_count"] += 1

            data["conversation_ids"].add(conversation_id)

            data["likes"] += tweet.get("likes", 0) or 0

            data["retweets"] += tweet.get("retweets", 0) or 0

            data["replies"] += tweet.get("replies", 0) or 0

            data["quotes"] += tweet.get("quotes", 0) or 0

            data["views"] += tweet.get("views", 0) or 0

            date = tweet.get("date")

            if date:
                if data["first_date"] is None or date < data["first_date"]:
                    data["first_date"] = date

                if data["last_date"] is None or date > data["last_date"]:
                    data["last_date"] = date

    result = []

    for username, data in users.items():
        result.append(
            {
                "username": username,
                "tweet_count": data["tweet_count"],
                "conversation_count": len(data["conversation_ids"]),
                "likes": data["likes"],
                "retweets": data["retweets"],
                "replies": data["replies"],
                "quotes": data["quotes"],
                "views": data["views"],
                "first_date": data["first_date"],
                "last_date": data["last_date"],
            }
        )

    result.sort(
        key=lambda user: user["tweet_count"],
        reverse=True,
    )

    return result


def save_jsonl(path, data):
    """Guarda una lista de diccionarios como JSONL."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for item in data:
            file.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main():

    print("=== PROCESAMIENTO ===")

    threads = load_jsonl(THREADS_FILE)

    print(f"Conversaciones cargadas: {len(threads)}")

    # ---------------------------------------------------------
    # Procesar conversaciones
    # ---------------------------------------------------------

    processed = []

    for thread in threads:
        result = process_thread(thread)

        if result is not None:
            processed.append(result)

    save_jsonl(
        PROCESSED_FILE,
        processed,
    )

    print(f"Conversaciones procesadas: {len(processed)}")

    # ---------------------------------------------------------
    # Procesar usuarios
    # ---------------------------------------------------------

    users = process_users(threads)

    save_jsonl(
        USERS_FILE,
        users,
    )

    print(f"Usuarios procesados: {len(users)}")

    print()
    print(f"Conversaciones: {PROCESSED_FILE}")

    print(f"Usuarios: {USERS_FILE}")


if __name__ == "__main__":
    main()
