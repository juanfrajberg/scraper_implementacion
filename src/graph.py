import json
from pathlib import Path

import networkx as nx

THREADS_FILE = Path("data/threads.jsonl")
GRAPH_FILE = Path("data/reply_graph.graphml")
FILTERED_GRAPH_FILE = Path("data/reply_graph_filtered.graphml")
COMMUNITIES_FILE = Path("data/communities.json")

MIN_EDGE_WEIGHT = 2
TOP_LIMIT = 20


def load_threads(path: Path) -> list[dict]:
    """Carga las conversaciones desde un archivo JSONL."""

    threads = []

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                threads.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return threads


def build_reply_graph(
    threads: list[dict],
) -> nx.DiGraph:
    """
    Construye un grafo dirigido de respuestas.

    Nodo:
        Una cuenta de X.

    Arista:
        A -> B significa que A respondió a B.

    Peso:
        Cantidad de respuestas de A hacia B.
    """

    graph = nx.DiGraph()

    for thread in threads:
        tweets = thread.get("tweets", [])

        for tweet in tweets:
            username = tweet.get("username")
            reply_to_user = tweet.get("in_reply_to_user")

            if not username or not reply_to_user:
                continue

            source = username
            target = reply_to_user

            if source == target:
                continue

            graph.add_node(source)
            graph.add_node(target)

            if graph.has_edge(source, target):
                graph[source][target]["weight"] += 1
            else:
                graph.add_edge(
                    source,
                    target,
                    weight=1,
                )

    return graph


def filter_graph(
    graph: nx.DiGraph,
    min_weight: int = MIN_EDGE_WEIGHT,
) -> nx.DiGraph:
    """
    Elimina las relaciones cuyo peso sea menor al mínimo indicado.
    """

    filtered = nx.DiGraph()

    for source, target, data in graph.edges(data=True):
        weight = data.get("weight", 1)

        if weight >= min_weight:
            filtered.add_edge(
                source,
                target,
                weight=weight,
            )

    # Eliminar nodos aislados.
    isolated = list(nx.isolates(filtered))
    filtered.remove_nodes_from(isolated)

    return filtered


def print_summary(
    graph: nx.DiGraph,
    threads: list[dict],
):
    """Muestra estadísticas básicas del grafo."""

    total_replies = sum(data["weight"] for _, _, data in graph.edges(data=True))

    print("=" * 70)
    print("GRAFO DE RESPUESTAS")
    print("=" * 70)

    print(f"Conversaciones: {len(threads)}")

    print(f"Cuentas: {graph.number_of_nodes()}")

    print(f"Conexiones: {graph.number_of_edges()}")

    print(f"Replies representados: {total_replies}")


def print_filtered_summary(
    graph: nx.DiGraph,
    min_weight: int,
):
    """Muestra estadísticas del grafo filtrado."""

    total_replies = sum(data["weight"] for _, _, data in graph.edges(data=True))

    print()
    print("=" * 70)
    print("GRAFO FILTRADO")
    print("=" * 70)

    print(f"Peso mínimo: {min_weight}")

    print(f"Cuentas: {graph.number_of_nodes()}")

    print(f"Conexiones: {graph.number_of_edges()}")

    print(f"Replies representados: {total_replies}")


def print_most_connected(
    graph: nx.DiGraph,
    limit: int = TOP_LIMIT,
):
    """Muestra las cuentas con más conexiones."""

    rankings = sorted(
        graph.degree(),
        key=lambda item: item[1],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"TOP {limit} - CUENTAS MÁS CONECTADAS")
    print("=" * 70)

    for position, (username, degree) in enumerate(
        rankings[:limit],
        start=1,
    ):
        print(f"{position:2}. conexiones={degree:4} | @{username}")


def print_most_replied(
    graph: nx.DiGraph,
    limit: int = TOP_LIMIT,
):
    """Muestra las cuentas que reciben más respuestas."""

    rankings = sorted(
        graph.in_degree(weight="weight"),
        key=lambda item: item[1],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"TOP {limit} - CUENTAS MÁS RESPONDIDAS")
    print("=" * 70)

    for position, (username, replies) in enumerate(
        rankings[:limit],
        start=1,
    ):
        accounts = graph.in_degree(username)

        print(
            f"{position:2}. replies_recibidos={int(replies):5} | cuentas={accounts:4} | @{username}"
        )


def print_most_replying(
    graph: nx.DiGraph,
    limit: int = TOP_LIMIT,
):
    """Muestra las cuentas que más respuestas realizan."""

    rankings = sorted(
        graph.out_degree(weight="weight"),
        key=lambda item: item[1],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"TOP {limit} - CUENTAS QUE MÁS RESPONDEN")
    print("=" * 70)

    for position, (username, replies) in enumerate(
        rankings[:limit],
        start=1,
    ):
        accounts = graph.out_degree(username)

        print(
            f"{position:2}. "
            f"replies_realizados={int(replies):5} | "
            f"cuentas={accounts:3} | "
            f"@{username}"
        )


def print_top_relationships(
    graph: nx.DiGraph,
    limit: int = TOP_LIMIT,
):
    """Muestra las relaciones con más respuestas."""

    relationships = sorted(
        graph.edges(data=True),
        key=lambda edge: edge[2]["weight"],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"TOP {limit} - RELACIONES DE REPLY")
    print("=" * 70)

    for position, (source, target, data) in enumerate(
        relationships[:limit],
        start=1,
    ):
        print(f"{position:2}. replies={data['weight']:5} | @{source} -> @{target}")


def print_top_reciprocal_relationships(
    graph: nx.DiGraph,
    limit: int = TOP_LIMIT,
):
    """Muestra las relaciones donde ambas cuentas se responden."""

    reciprocal = []

    for source, target, data in graph.edges(data=True):
        if not graph.has_edge(target, source):
            continue

        # Evitar mostrar A -> B y B -> A por separado.
        if source >= target:
            continue

        forward = data["weight"]
        backward = graph[target][source]["weight"]
        total = forward + backward

        reciprocal.append(
            (
                total,
                source,
                target,
                forward,
                backward,
            )
        )

    reciprocal.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"TOP {limit} - RELACIONES RECÍPROCAS")
    print("=" * 70)

    for position, (
        total,
        source,
        target,
        forward,
        backward,
    ) in enumerate(
        reciprocal[:limit],
        start=1,
    ):
        print(
            f"{position:2}. "
            f"total={total:4} | "
            f"@{source} -> @{target}: {forward} | "
            f"@{target} -> @{source}: {backward}"
        )


def calculate_reciprocity(
    graph: nx.DiGraph,
) -> float:
    """
    Calcula qué proporción de las conexiones dirigidas
    pertenecen a relaciones donde existe respuesta en ambos sentidos.
    """

    if graph.number_of_edges() == 0:
        return 0.0

    reciprocal_edges = 0

    for source, target in graph.edges():
        if graph.has_edge(target, source):
            reciprocal_edges += 1

    return reciprocal_edges / graph.number_of_edges()


def classify_community(
    community_graph: nx.DiGraph,
    concentration: float,
    density: float,
    reciprocity: float,
) -> str:
    """
    Clasifica una comunidad según su estructura.

    La clasificación es descriptiva, no pretende determinar
    automáticamente el significado social de la comunidad.
    """

    node_count = community_graph.number_of_nodes()

    if node_count <= 1:
        return "CUENTA AISLADA"

    if concentration >= 0.50:
        return "CENTRADA EN UNA CUENTA"

    if reciprocity >= 0.30 and density >= 0.10:
        return "RECÍPROCA Y COHESIONADA"

    if reciprocity >= 0.30:
        return "RECÍPROCA"

    if density >= 0.15:
        return "COHESIONADA"

    if density < 0.05:
        return "POCO COHESIONADA"

    return "INTERMEDIA"


def analyze_community(
    graph: nx.DiGraph,
    community_nodes: set[str],
) -> dict:
    """
    Calcula las métricas principales de una comunidad.
    """

    community_graph = graph.subgraph(community_nodes).copy()

    node_count = community_graph.number_of_nodes()
    edge_count = community_graph.number_of_edges()

    total_replies = sum(data["weight"] for _, _, data in community_graph.edges(data=True))

    # Densidad dirigida.
    density = nx.density(community_graph) if node_count > 1 else 0.0

    # Reciprocidad.
    reciprocity = calculate_reciprocity(community_graph)

    # Interacciones de cada cuenta:
    # respuestas realizadas + respuestas recibidas.
    interactions = {}

    for username in community_graph.nodes():
        received = community_graph.in_degree(
            username,
            weight="weight",
        )

        sent = community_graph.out_degree(
            username,
            weight="weight",
        )

        interactions[username] = int(received + sent)

    ranking = sorted(
        interactions.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_account = ranking[0][0]
    main_interactions = ranking[0][1]

    # Concentración de la comunidad:
    # porcentaje de las interacciones que corresponden
    # a la cuenta principal.
    concentration = main_interactions / (total_replies * 2) if total_replies > 0 else 0.0

    # Grado promedio ponderado.
    average_degree = sum(interactions.values()) / node_count if node_count > 0 else 0.0

    # Relaciones principales.
    relationships = []

    for source, target, data in community_graph.edges(data=True):
        relationships.append(
            {
                "source": source,
                "target": target,
                "weight": int(data["weight"]),
            }
        )

    relationships.sort(
        key=lambda item: item["weight"],
        reverse=True,
    )

    community_type = classify_community(
        community_graph,
        concentration,
        density,
        reciprocity,
    )

    return {
        "accounts": node_count,
        "replies_internal": total_replies,
        "connections": edge_count,
        "density": round(density, 4),
        "reciprocity": round(reciprocity, 4),
        "average_degree": round(
            average_degree,
            2,
        ),
        "main_account": main_account,
        "main_account_interactions": main_interactions,
        "concentration": round(
            concentration,
            4,
        ),
        "type": community_type,
        "top_accounts": [
            {
                "username": username,
                "interactions": interactions,
            }
            for username, interactions in ranking[:10]
        ],
        "top_relationships": relationships[:10],
    }


def detect_communities(
    graph: nx.DiGraph,
) -> list[set[str]]:
    """
    Detecta comunidades utilizando Louvain sobre una versión
    no dirigida del grafo.

    Se ignora la dirección únicamente para detectar comunidades.
    Las métricas posteriores conservan la dirección original.
    """

    undirected = graph.to_undirected()

    if undirected.number_of_nodes() == 0:
        return []

    communities = nx.community.louvain_communities(
        undirected,
        weight="weight",
        seed=42,
    )

    communities.sort(
        key=len,
        reverse=True,
    )

    return communities


def analyze_communities(
    graph: nx.DiGraph,
) -> list[dict]:
    """Detecta y analiza todas las comunidades."""

    communities = detect_communities(graph)

    results = []

    for community_id, nodes in enumerate(
        communities,
        start=1,
    ):
        analysis = analyze_community(
            graph,
            nodes,
        )

        analysis["community"] = community_id

        results.append(analysis)

    return results


def print_communities(
    communities: list[dict],
    limit: int = TOP_LIMIT,
):
    """Muestra las principales comunidades."""

    print()
    print("=" * 70)
    print(f"TOP {limit} - COMUNIDADES")
    print("=" * 70)

    print(f"Comunidades detectadas: {len(communities)}")

    for community in communities[:limit]:
        print()
        print(f"COMUNIDAD {community['community']}")

        print(f"  cuentas={community['accounts']}")

        print(f"  replies internos={community['replies_internal']}")

        print(f"  conexiones={community['connections']}")

        print(f"  densidad={community['density']:.4f}")

        print(f"  reciprocidad={community['reciprocity']:.2%}")

        print(f"  grado promedio={community['average_degree']:.2f}")

        print(f"  cuenta principal=@{community['main_account']}")

        print(f"  interacciones principales={community['main_account_interactions']}")

        print(f"  concentración={community['concentration']:.2%}")

        print(f"  tipo={community['type']}")

        print("  principales cuentas:")

        for account in community["top_accounts"]:
            print(f"    @{account['username']}: {account['interactions']} interacciones")

        print("  relaciones principales:")

        for relationship in community["top_relationships"][:5]:
            print(
                f"    "
                f"@{relationship['source']} "
                f"-> "
                f"@{relationship['target']}: "
                f"{relationship['weight']}"
            )


def save_graph(
    graph: nx.DiGraph,
    path: Path,
):
    """Guarda el grafo en formato GraphML."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    nx.write_graphml(
        graph,
        path,
    )

    print()
    print(f"Grafo guardado en: {path}")


def save_communities(
    communities: list[dict],
    path: Path,
):
    """Guarda el análisis de comunidades en JSON."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            communities,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(f"Comunidades guardadas en: {path}")


def main():
    print("=" * 70)
    print("ANÁLISIS DEL GRAFO DE RESPUESTAS")
    print("=" * 70)

    threads = load_threads(THREADS_FILE)

    print(f"Threads cargados: {len(threads)}")

    # --------------------------------------------------
    # GRAFO ORIGINAL
    # --------------------------------------------------

    graph = build_reply_graph(threads)

    print_summary(
        graph,
        threads,
    )

    print_most_connected(graph)

    print_most_replied(graph)

    print_most_replying(graph)

    print_top_relationships(graph)

    print_top_reciprocal_relationships(graph)

    save_graph(
        graph,
        GRAPH_FILE,
    )

    # --------------------------------------------------
    # GRAFO FILTRADO
    # --------------------------------------------------

    filtered_graph = filter_graph(
        graph,
        MIN_EDGE_WEIGHT,
    )

    print_filtered_summary(
        filtered_graph,
        MIN_EDGE_WEIGHT,
    )

    save_graph(
        filtered_graph,
        FILTERED_GRAPH_FILE,
    )

    # --------------------------------------------------
    # COMUNIDADES
    # --------------------------------------------------

    communities = analyze_communities(filtered_graph)

    print_communities(communities)

    save_communities(
        communities,
        COMMUNITIES_FILE,
    )


if __name__ == "__main__":
    main()
