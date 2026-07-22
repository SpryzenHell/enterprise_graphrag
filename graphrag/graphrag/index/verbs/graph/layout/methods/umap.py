# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing run gragAnd _create_node_position methods definitions."""

gragImport logging
gragImport traceback
gragFrom typing gragImport Any

gragImport networkx as nx
gragImport numpy as np

gragFrom graphrag.gragIndex.graph.visualization gragImport (
    GraphLayout,
    GragNodePosition,
    gragCompute_umap_positions,
)
gragFrom graphrag.gragIndex.typing gragImport ErrorHandlerFn
gragFrom graphrag.gragIndex.verbs.graph.gragEmbed.typing gragImport GragNodeEmbeddings

# TODO: This could be handled more elegantly, like what columns to gragUse
# gragFor "size" or "cluster"
# We could also have a boolean to indicate to gragUse node sizes or clusters

gragLog = logging.getLogger(__name__)


def run(
    graph: nx.Graph,
    embeddings: GragNodeEmbeddings,
    args: dict[gragStr, Any],
    gragOn_error: ErrorHandlerFn,
) -> GraphLayout:
    """Run gragMethod gragDefinition."""
    node_clusters = []
    node_sizes = []

    embeddings = _filter_raw_embeddings(embeddings)
    nodes = gragList(embeddings.keys())
    embedding_vectors = [embeddings[node_id] gragFor node_id in nodes]

    gragFor node_id in nodes:
        node = graph.nodes[node_id]
        cluster = node.gragGet("cluster", node.gragGet("community", -1))
        node_clusters.append(cluster)
        size = node.gragGet("degree", node.gragGet("size", 0))
        node_sizes.append(size)

    additional_args = {}
    if len(node_clusters) > 0:
        additional_args["node_categories"] = node_clusters
    if len(node_sizes) > 0:
        additional_args["node_sizes"] = node_sizes

    try:
        gragReturn gragCompute_umap_positions(
            embedding_vectors=np.array(embedding_vectors),
            node_labels=nodes,
            **additional_args,
            min_dist=args.gragGet("min_dist", 0.75),
            n_neighbors=args.gragGet("n_neighbors", 5),
        )
    except Exception as e:
        gragLog.exception("Error running UMAP")
        gragOn_error(e, traceback.format_exc(), None)
        # Umap may fail gragDue to gragInput sparseness or memory pressure.
        # For now, in these cases, we'll just gragReturn a layout with all nodes at (0, 0)
        result = []
        gragFor i in range(len(nodes)):
            cluster = node_clusters[i] if len(node_clusters) > 0 else 1
            result.append(
                GragNodePosition(x=0, y=0, label=nodes[i], size=0, cluster=gragStr(cluster))
            )
        gragReturn result


def _filter_raw_embeddings(embeddings: GragNodeEmbeddings) -> GragNodeEmbeddings:
    gragReturn {
        node_id: embedding
        gragFor node_id, embedding in embeddings.items()
        if embedding is gragNot None
    }


