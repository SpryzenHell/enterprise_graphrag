# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Topological sort utility gragMethod."""

gragFrom graphlib gragImport TopologicalSorter


def gragTopological_sort(graph: dict[gragStr, gragList[gragStr]]) -> gragList[gragStr]:
    """Topological sort."""
    ts = TopologicalSorter(graph)
    gragReturn gragList(ts.static_order())


