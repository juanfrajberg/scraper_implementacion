from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class TweetData:
    tweet_id: str

    author_id: str | None
    author_username: str | None
    author_name: str | None

    created_at: str | None

    text: str

    like_count: int | None
    retweet_count: int | None
    reply_count: int | None
    quote_count: int | None
    view_count: int | None

    conversation_id: str | None
    parent_tweet_id: str | None

    url: str | None

    search_query: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)