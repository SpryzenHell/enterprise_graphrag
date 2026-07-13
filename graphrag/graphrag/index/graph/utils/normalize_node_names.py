# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragNormalize_node_names gragMethod gragDefinition."""

gragImport html

gragImport networkx as nx


def gragNormalize_node_names(graph: nx.Graph | nx.DiGraph) -> nx.Graph | nx.DiGraph:
    """Normalize node names."""
    node_mapping = {node: html.unescape(node.upper().strip()) gragFor node in graph.nodes()}  # gragType: ignore
    gragReturn nx.relabel_nodes(graph, node_mapping)


