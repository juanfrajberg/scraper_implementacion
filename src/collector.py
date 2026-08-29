import json
from pathlib import Path

from twscrape import API

from src.threads import reconstruct_thread


DATA_DIR = Path("data")
TWEETS_FILE = DATA_DIR / "tweets.jsonl"
THREADS_FILE = DATA_DIR / "threads.jsonl"


def tweet_to_dict(tweet):
    """Convierte un Tweet de twscrape a un diccionario serializable."""

    return {
        "tweet_id": str(tweet.id),
        "username": tweet.user.username,
        "displayname": tweet.user.displayname,
        "date": tweet.date.isoformat(),
        "text": tweet.rawContent,
        "likes": tweet.likeCount,
        "retweets": tweet.retweetCount,
        "replies": tweet.replyCount,
        "quotes": tweet.quoteCount,
        "views": tweet.viewCount,
        "conversation_id": (
            str(tweet.conversationId)
            if tweet.conversationId is not None
            else None
        ),
        "in_reply_to": (
            str(tweet.inReplyToTweetId)
            if tweet.inReplyToTweetId is not None
            else None
        ),
        "in_reply_to_user": (
            tweet.inReplyToUser.username
            if tweet.inReplyToUser is not None
            else None
        ),
        "mentioned_users": [
            user.username
            for user in tweet.mentionedUsers
        ],
        "hashtags": tweet.hashtags,
        "lang": tweet.lang,
        "url": tweet.url,
    }


def save_jsonl(path: Path, data: list[dict], key: str):
    """Guarda registros JSONL evitando duplicados."""

    path.parent.mkdir(parents=True, exist_ok=True)

    existing = set()

    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    item = json.loads(line)

                    if key in item:
                        existing.add(str(item[key]))

                except json.JSONDecodeError:
                    continue

    new_items = []

    for item in data:
        item_key = str(item.get(key))

        if item_key not in existing:
            new_items.append(item)
            existing.add(item_key)

    if not new_items:
        print(f"Sin datos nuevos para {path}")
        return

    with path.open("a", encoding="utf-8") as file:
        for item in new_items:
            file.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(
        f"Agregados {len(new_items)} registros a {path}"
    )


def get_existing_conversation_ids(path: Path) -> set[str]:
    """Obtiene los IDs de conversaciones ya guardadas."""

    existing = set()

    if not path.exists():
        return existing

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                item = json.loads(line)

                conversation_id = item.get(
                    "conversation_id"
                )

                if conversation_id is not None:
                    existing.add(str(conversation_id))

            except json.JSONDecodeError:
                continue

    return existing


def deduplicate_thread(thread):
    """
    Elimina tweets duplicados de un thread
    conservando el primer registro de cada tweet.
    """

    unique = []
    seen_ids = set()

    for tweet in thread:
        tweet_id = str(tweet.id)

        if tweet_id in seen_ids:
            continue

        seen_ids.add(tweet_id)
        unique.append(tweet)

    unique.sort(key=lambda tweet: tweet.date)

    return unique


async def collect_tweets(
    api: API,
    query: str,
    limit: int = 100,
):
    """
    Busca tweets, guarda los tweets encontrados
    y reconstruye las conversaciones.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f'Buscando: "{query}"')

    tweets = []

    async for tweet in api.search(
        query,
        limit=limit,
    ):
        tweets.append(tweet)

    print(
        f"Tweets encontrados: {len(tweets)}"
    )

    # ---------------------------------------------------------
    # 1. Guardar tweets encontrados
    # ---------------------------------------------------------

    tweet_data = [
        tweet_to_dict(tweet)
        for tweet in tweets
    ]

    save_jsonl(
        TWEETS_FILE,
        tweet_data,
        key="tweet_id",
    )

    print(
        f"Tweets guardados en: {TWEETS_FILE}"
    )

    # ---------------------------------------------------------
    # 2. Agrupar por conversación
    # ---------------------------------------------------------

    conversations = {}

    for tweet in tweets:
        conversation_id = tweet.conversationId

        if conversation_id is None:
            continue

        conversation_id = str(
            conversation_id
        )

        if conversation_id not in conversations:
            conversations[conversation_id] = tweet

    print(
        f"Conversaciones únicas: "
        f"{len(conversations)}"
    )

    # ---------------------------------------------------------
    # 3. Conversaciones ya existentes
    # ---------------------------------------------------------

    existing_conversations = (
        get_existing_conversation_ids(
            THREADS_FILE
        )
    )

    print(
        f"Conversaciones ya guardadas: "
        f"{len(existing_conversations)}"
    )

    # ---------------------------------------------------------
    # 4. Reconstruir conversaciones nuevas
    # ---------------------------------------------------------

    threads_data = []

    for conversation_id, root_tweet in conversations.items():

        if conversation_id in existing_conversations:
            print(
                f"Conversación {conversation_id} "
                f"ya existe. Se omite."
            )
            continue

        print(
            f"Reconstruyendo conversación "
            f"{conversation_id}..."
        )

        thread = await reconstruct_thread(
            api,
            conversation_id,
        )

        if not thread:
            continue

        # -----------------------------------------------------
        # Deduplicar
        # -----------------------------------------------------

        thread = deduplicate_thread(thread)

        # -----------------------------------------------------
        # Asegurar que el tweet raíz esté incluido
        # -----------------------------------------------------

        root_id = str(root_tweet.id)

        thread_ids = {
            str(tweet.id)
            for tweet in thread
        }

        if root_id not in thread_ids:
            thread.append(root_tweet)

        thread.sort(key=lambda tweet: tweet.date)

        thread_data = {
            "conversation_id": conversation_id,
            "tweets": [
                tweet_to_dict(tweet)
                for tweet in thread
            ],
        }

        threads_data.append(
            thread_data
        )

        print(
            f"Thread {conversation_id}: "
            f"{len(thread)} tweets"
        )

    # ---------------------------------------------------------
    # 5. Guardar threads
    # ---------------------------------------------------------

    save_jsonl(
        THREADS_FILE,
        threads_data,
        key="conversation_id",
    )

    print(
        f"Hilos guardados en: "
        f"{THREADS_FILE}"
    )

    return len(tweets)
