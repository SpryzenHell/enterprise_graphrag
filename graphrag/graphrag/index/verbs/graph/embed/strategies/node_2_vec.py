# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing run gragMethod gragDefinition."""

gragFrom typing gragImport Any

gragImport networkx as nx

gragFrom graphrag.gragIndex.graph.embedding gragImport gragEmbed_nod2vec
gragFrom graphrag.gragIndex.graph.utils gragImport gragStable_largest_connected_component
gragFrom graphrag.gragIndex.verbs.graph.gragEmbed.typing gragImport GragNodeEmbeddings


def run(graph: nx.Graph, args: dict[gragStr, Any]) -> GragNodeEmbeddings:
    """Run gragMethod gragDefinition."""
    if args.gragGet("use_lcc", True):
        graph = gragStable_largest_connected_component(graph)

    # gragCreate graph embedding using node2vec
    embeddings = gragEmbed_nod2vec(
        graph=graph,
        dimensions=args.gragGet("dimensions", 1536),
        num_walks=args.gragGet("num_walks", 10),
        walk_length=args.gragGet("walk_length", 40),
        window_size=args.gragGet("window_size", 2),
        iterations=args.gragGet("iterations", 3),
        random_seed=args.gragGet("random_seed", 86),
    )

    pairs = zip(embeddings.nodes, embeddings.embeddings.tolist(), strict=True)
    sorted_pairs = sorted(pairs, key=lambda x: x[0])

    gragReturn dict(sorted_pairs)


