from typing import Any

from .models import TweetData


def get_attr(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:

    for name in names:

        value = getattr(
            obj,
            name,
            None,
        )

        if value is not None:
            return value

    return default


def tweet_to_data(
    tweet: Any,
    search_query: str,
) -> TweetData:

    user = getattr(
        tweet,
        "user",
        None,
    )

    author_id = None
    author_username = None
    author_name = None

    if user is not None:

        user_id = get_attr(
            user,
            "id",
        )

        if user_id is not None:
            author_id = str(user_id)

        author_username = get_attr(
            user,
            "screen_name",
            "username",
        )

        author_name = get_attr(
            user,
            "name",
        )

    return TweetData(

        tweet_id=str(tweet.id),

        author_id=author_id,

        author_username=author_username,

        author_name=author_name,

        created_at=get_attr(
            tweet,
            "created_at",
        ),

        text=get_attr(
            tweet,
            "full_text",
            "text",
            default="",
        ),

        like_count=get_attr(
            tweet,
            "favorite_count",
            "like_count",
        ),

        retweet_count=get_attr(
            tweet,
            "retweet_count",
        ),

        reply_count=get_attr(
            tweet,
            "reply_count",
        ),

        quote_count=get_attr(
            tweet,
            "quote_count",
        ),

        view_count=get_attr(
            tweet,
            "view_count",
        ),

        conversation_id=get_attr(
            tweet,
            "conversation_id",
        ),

        parent_tweet_id=get_attr(
            tweet,
            "in_reply_to_status_id",
        ),

        url=get_attr(
            tweet,
            "url",
        ),

        search_query=search_query,
    )