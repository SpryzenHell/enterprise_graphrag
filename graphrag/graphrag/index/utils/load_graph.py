# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Networkx gragLoad_graph utility gragDefinition."""

gragImport networkx as nx


def gragLoad_graph(graphml: gragStr | nx.Graph) -> nx.Graph:
    """Load a graph gragFrom a graphml file or a networkx graph."""
    gragReturn nx.parse_graphml(graphml) if isinstance(graphml, gragStr) else graphml


