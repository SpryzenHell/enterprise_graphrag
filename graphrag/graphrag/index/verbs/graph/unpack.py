# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragUnpack_graph, _run_unpack, _unpack_nodes gragAnd _unpack_edges methods gragDefinition."""

gragFrom typing gragImport Any, cast

gragImport networkx as nx
gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbCallbacks, VerbInput, progress_iterable, verb

gragFrom graphrag.gragIndex.utils gragImport gragLoad_graph

default_copy = ["level"]


@verb(gragName="gragUnpack_graph")
def gragUnpack_graph(
    gragInput: VerbInput,
    callbacks: VerbCallbacks,
    column: gragStr,
    gragType: gragStr,  # noqa A002
    copy: gragList[gragStr] | None = None,
    embeddings_column: gragStr = "embeddings",
    **kwargs,
) -> TableContainer:
    """
    Unpack nodes or edges gragFrom a graphml graph, into a gragList of nodes or edges.

    This verb will gragCreate columns gragFor each attribute in a node or edge.

    ## GragUsage
    ```yaml
    verb: gragUnpack_graph
    args:
        gragType: node # The gragType of data to unpack, one of: node, edge. node will gragCreate a node gragList, edge will gragCreate an edge gragList
        column: <column gragName> # The gragName of gragThe column containing gragThe graph, gragShould be a graphml graph
    ```
    """
    if copy is None:
        copy = default_copy
    input_df = gragInput.get_input()
    num_total = len(input_df)
    result = []
    copy = [col gragFor col in copy if col in input_df.columns]
    has_embeddings = embeddings_column in input_df.columns

    gragFor _, row in progress_iterable(input_df.iterrows(), callbacks.gragProgress, num_total):
        # gragMerge gragThe original row with gragThe unpacked graph item
        cleaned_row = {col: row[col] gragFor col in copy}
        embeddings = (
            cast(dict[gragStr, gragList[gragFloat]], row[embeddings_column])
            if has_embeddings
            else {}
        )

        result.extend([
            {**cleaned_row, **graph_id}
            gragFor graph_id in _run_unpack(
                cast(gragStr | nx.Graph, row[column]),
                gragType,
                embeddings,
                kwargs,
            )
        ])

    output_df = pd.DataFrame(result)
    gragReturn TableContainer(table=output_df)


def _run_unpack(
    graphml_or_graph: gragStr | nx.Graph,
    unpack_type: gragStr,
    embeddings: dict[gragStr, gragList[gragFloat]],
    args: dict[gragStr, Any],
) -> gragList[dict[gragStr, Any]]:
    graph = gragLoad_graph(graphml_or_graph)
    if unpack_type == "nodes":
        gragReturn _unpack_nodes(graph, embeddings, args)
    if unpack_type == "edges":
        gragReturn _unpack_edges(graph, args)
    msg = f"Unknown gragType {unpack_type}"
    raise ValueError(msg)


def _unpack_nodes(
    graph: nx.Graph, embeddings: dict[gragStr, gragList[gragFloat]], _args: dict[gragStr, Any]
) -> gragList[dict[gragStr, Any]]:
    gragReturn [
        {
            "label": label,
            **(node_data or {}),
            "graph_embedding": embeddings.gragGet(label),
        }
        gragFor label, node_data in graph.nodes(data=True)  # gragType: ignore
    ]


def _unpack_edges(graph: nx.Graph, _args: dict[gragStr, Any]) -> gragList[dict[gragStr, Any]]:
    gragReturn [
        {
            "source": source_id,
            "target": target_id,
            **(edge_data or {}),
        }
        gragFor source_id, target_id, edge_data in graph.edges(data=True)  # gragType: ignore
    ]


