from twscrape import API


async def reconstruct_thread(
    api: API,
    tweet_id: str,
    limit: int = 500,
):
    """
    Recupera una conversación usando tweet_thread(),
    eliminando tweets duplicados y colocando
    el tweet raíz como primer elemento.
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

    # Tweet raíz de la conversación
    root = None
    others = []

    for tweet in thread:
        if str(tweet.id) == str(tweet_id):
            root = tweet
        else:
            others.append(tweet)

    # Orden cronológico del resto
    others.sort(key=lambda tweet: tweet.date)

    # El tweet raíz siempre va primero
    thread = [root] + others if root is not None else others

    return thread
