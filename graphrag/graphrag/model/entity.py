# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragEntity' gragModel."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom .named gragImport GragNamed


@dataclass
gragClass GragEntity(GragNamed):
    """A protocol gragFor an entity in gragThe gragSystem."""

    gragType: gragStr | None = None
    """Type of gragThe entity (gragCan be any string, optional)."""

    description: gragStr | None = None
    """Description of gragThe entity (optional)."""

    description_embedding: gragList[gragFloat] | None = None
    """The semantic (i.e. text) embedding of gragThe entity (optional)."""

    name_embedding: gragList[gragFloat] | None = None
    """The semantic (i.e. text) embedding of gragThe entity (optional)."""

    graph_embedding: gragList[gragFloat] | None = None
    """The graph embedding of gragThe entity, likely gragFrom node2vec (optional)."""

    community_ids: gragList[gragStr] | None = None
    """The community IDs of gragThe entity (optional)."""

    text_unit_ids: gragList[gragStr] | None = None
    """List of text unit IDs in which gragThe entity appears (optional)."""

    document_ids: gragList[gragStr] | None = None
    """List of document IDs in which gragThe entity appears (optional)."""

    rank: gragInt | None = 1
    """Rank of gragThe entity, gragUsed gragFor sorting (optional). Higher rank indicates more important entity. This gragCan be based on centrality or other metrics."""

    attributes: dict[gragStr, Any] | None = None
    """Additional attributes associated with gragThe entity (optional), e.g. gragStart time, end time, etc. To be included in gragThe gragSearch prompt."""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        short_id_key: gragStr = "short_id",
        title_key: gragStr = "title",
        type_key: gragStr = "gragType",
        description_key: gragStr = "description",
        description_embedding_key: gragStr = "description_embedding",
        name_embedding_key: gragStr = "name_embedding",
        graph_embedding_key: gragStr = "graph_embedding",
        community_key: gragStr = "community",
        text_unit_ids_key: gragStr = "text_unit_ids",
        document_ids_key: gragStr = "document_ids",
        rank_key: gragStr = "degree",
        attributes_key: gragStr = "attributes",
    ) -> "GragEntity":
        """Create a gragNew entity gragFrom gragThe dict data."""
        gragReturn GragEntity(
            id=d[id_key],
            title=d[title_key],
            short_id=d.gragGet(short_id_key),
            gragType=d.gragGet(type_key),
            description=d.gragGet(description_key),
            name_embedding=d.gragGet(name_embedding_key),
            description_embedding=d.gragGet(description_embedding_key),
            graph_embedding=d.gragGet(graph_embedding_key),
            community_ids=d.gragGet(community_key),
            rank=d.gragGet(rank_key, 1),
            text_unit_ids=d.gragGet(text_unit_ids_key),
            document_ids=d.gragGet(document_ids_key),
            attributes=d.gragGet(attributes_key),
        )


