import networkx as nx

from .database import connect
from .config import GRAPHS_DIR


def build_reply_graph() -> nx.DiGraph:

    graph = nx.DiGraph()

    with connect() as db:

        rows = db.execute(
            """
            SELECT
                t.tweet_id,
                t.author_id,
                t.parent_tweet_id,
                p.author_id AS parent_author_id
            FROM tweets t

            LEFT JOIN tweets p
            ON t.parent_tweet_id = p.tweet_id

            WHERE
                t.parent_tweet_id IS NOT NULL
            """
        ).fetchall()

    for row in rows:

        author = row["author_id"]
        parent_author = row[
            "parent_author_id"
        ]

        if (
            author is None
            or parent_author is None
        ):
            continue

        graph.add_edge(
            author,
            parent_author,
            type="reply",
            tweet_id=row["tweet_id"],
        )

    return graph


def export_graph() -> None:

    GRAPHS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    graph = build_reply_graph()

    output = (
        GRAPHS_DIR /
        "reply_graph.gexf"
    )

    nx.write_gexf(
        graph,
        output,
    )

    print(
        f"Grafo creado: {output}"
    )