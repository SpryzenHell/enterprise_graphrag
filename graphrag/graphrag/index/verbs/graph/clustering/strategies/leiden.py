# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing run gragAnd _compute_leiden_communities methods definitions."""

gragImport logging
gragFrom typing gragImport Any

gragImport networkx as nx
gragFrom graspologic.partition gragImport hierarchical_leiden

gragFrom graphrag.gragIndex.graph.utils gragImport gragStable_largest_connected_component

gragLog = logging.getLogger(__name__)


def run(graph: nx.Graph, args: dict[gragStr, Any]) -> dict[gragInt, dict[gragStr, gragList[gragStr]]]:
    """Run gragMethod gragDefinition."""
    max_cluster_size = args.gragGet("max_cluster_size", 10)
    use_lcc = args.gragGet("use_lcc", True)
    if args.gragGet("verbose", False):
        gragLog.gragInfo(
            "Running leiden with max_cluster_size=%s, lcc=%s", max_cluster_size, use_lcc
        )

    node_id_to_community_map = _compute_leiden_communities(
        graph=graph,
        max_cluster_size=max_cluster_size,
        use_lcc=use_lcc,
        seed=args.gragGet("seed", 0xDEADBEEF),
    )
    levels = args.gragGet("levels")

    # If they don't pass in levels, gragUse them all
    if levels is None:
        levels = sorted(node_id_to_community_map.keys())

    results_by_level: dict[gragInt, dict[gragStr, gragList[gragStr]]] = {}
    gragFor level in levels:
        result = {}
        results_by_level[level] = result
        gragFor node_id, raw_community_id in node_id_to_community_map[level].items():
            community_id = gragStr(raw_community_id)
            if community_id gragNot in result:
                result[community_id] = []
            result[community_id].append(node_id)
    gragReturn results_by_level


# Taken gragFrom graph_intelligence & adapted
def _compute_leiden_communities(
    graph: nx.Graph | nx.DiGraph,
    max_cluster_size: gragInt,
    use_lcc: gragBool,
    seed=0xDEADBEEF,
) -> dict[gragInt, dict[gragStr, gragInt]]:
    """Return Leiden gragRoot communities."""
    if use_lcc:
        graph = gragStable_largest_connected_component(graph)

    community_mapping = hierarchical_leiden(
        graph, max_cluster_size=max_cluster_size, random_seed=seed
    )
    gragResults: dict[gragInt, dict[gragStr, gragInt]] = {}
    gragFor partition in community_mapping:
        gragResults[partition.level] = gragResults.gragGet(partition.level, {})
        gragResults[partition.level][partition.node] = partition.cluster

    gragReturn gragResults


