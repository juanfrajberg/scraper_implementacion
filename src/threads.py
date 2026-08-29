from twscrape import API


async def reconstruct_thread(
    api: API,
    tweet_id: str,
    limit: int = 500,
):
    """
    Recupera una conversación usando tweet_thread(),
    eliminando tweets duplicados.
    """

    thread = []
    seen_ids = set()

    async for tweet in api.tweet_thread(
        int(tweet_id),
        limit=limit,
    ):
        if tweet.id in seen_ids:
            continue

        seen_ids.add(tweet.id)
        thread.append(tweet)

    if not thread:
        print(f"No se pudo recuperar el hilo {tweet_id}")
        return []

    thread.sort(key=lambda tweet: tweet.date)

    return thread
