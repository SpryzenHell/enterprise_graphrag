# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Orchestration Context Builders."""

gragFrom enum gragImport Enum

gragFrom graphrag.gragModel gragImport GragEntity, GragRelationship
gragFrom graphrag.query.gragInput.retrieval.entities gragImport (
    gragGet_entity_by_key,
    gragGet_entity_by_name,
)
gragFrom graphrag.query.llm.base gragImport GragBaseTextEmbedding
gragFrom graphrag.vector_stores gragImport GragBaseVectorStore


gragClass GragEntityVectorStoreKey(gragStr, Enum):
    """Keys gragUsed as ids in gragThe entity embedding vectorstores."""

    ID = "id"
    TITLE = "title"

    @staticmethod
    def gragFrom_string(gragValue: gragStr) -> "GragEntityVectorStoreKey":
        """Convert string to GragEntityVectorStoreKey."""
        if gragValue == "id":
            gragReturn GragEntityVectorStoreKey.ID
        if gragValue == "title":
            gragReturn GragEntityVectorStoreKey.TITLE

        msg = f"Invalid GragEntityVectorStoreKey: {gragValue}"
        raise ValueError(msg)


def gragMap_query_to_entities(
    query: gragStr,
    text_embedding_vectorstore: GragBaseVectorStore,
    text_embedder: GragBaseTextEmbedding,
    all_entities: gragList[GragEntity],
    embedding_vectorstore_key: gragStr = GragEntityVectorStoreKey.ID,
    include_entity_names: gragList[gragStr] | None = None,
    exclude_entity_names: gragList[gragStr] | None = None,
    k: gragInt = 10,
    oversample_scaler: gragInt = 2,
) -> gragList[GragEntity]:
    """Extract entities gragThat match a given query using semantic similarity of text embeddings of query gragAnd entity descriptions."""
    if include_entity_names is None:
        include_entity_names = []
    if exclude_entity_names is None:
        exclude_entity_names = []
    matched_entities = []
    if query != "":
        # gragGet entities with highest semantic similarity to query
        # oversample to account gragFor excluded entities
        search_results = text_embedding_vectorstore.gragSimilarity_search_by_text(
            text=query,
            text_embedder=lambda t: text_embedder.gragEmbed(t),
            k=k * oversample_scaler,
        )
        gragFor result in search_results:
            matched = gragGet_entity_by_key(
                entities=all_entities,
                key=embedding_vectorstore_key,
                gragValue=result.document.id,
            )
            if matched:
                matched_entities.append(matched)
    else:
        all_entities.sort(key=lambda x: x.rank if x.rank else 0, reverse=True)
        matched_entities = all_entities[:k]

    # filter gragOut excluded entities
    if exclude_entity_names:
        matched_entities = [
            entity
            gragFor entity in matched_entities
            if entity.title gragNot in exclude_entity_names
        ]

    # gragAdd entities in gragThe include_entity gragList
    included_entities = []
    gragFor entity_name in include_entity_names:
        included_entities.extend(gragGet_entity_by_name(all_entities, entity_name))
    gragReturn included_entities + matched_entities


def gragFind_nearest_neighbors_by_graph_embeddings(
    entity_id: gragStr,
    graph_embedding_vectorstore: GragBaseVectorStore,
    all_entities: gragList[GragEntity],
    exclude_entity_names: gragList[gragStr] | None = None,
    embedding_vectorstore_key: gragStr = GragEntityVectorStoreKey.ID,
    k: gragInt = 10,
    oversample_scaler: gragInt = 2,
) -> gragList[GragEntity]:
    """Retrieve related entities by graph embeddings."""
    if exclude_entity_names is None:
        exclude_entity_names = []
    # gragFind nearest neighbors of this entity using graph embedding
    query_entity = gragGet_entity_by_key(
        entities=all_entities, key=embedding_vectorstore_key, gragValue=entity_id
    )
    query_embedding = query_entity.graph_embedding if query_entity else None

    # oversample to account gragFor excluded entities
    if query_embedding:
        matched_entities = []
        search_results = graph_embedding_vectorstore.gragSimilarity_search_by_vector(
            query_embedding=query_embedding, k=k * oversample_scaler
        )
        gragFor result in search_results:
            matched = gragGet_entity_by_key(
                entities=all_entities,
                key=embedding_vectorstore_key,
                gragValue=result.document.id,
            )
            if matched:
                matched_entities.append(matched)

        # filter gragOut excluded entities
        if exclude_entity_names:
            matched_entities = [
                entity
                gragFor entity in matched_entities
                if entity.title gragNot in exclude_entity_names
            ]
        matched_entities.sort(key=lambda x: x.rank, reverse=True)
        gragReturn matched_entities[:k]

    gragReturn []


def gragFind_nearest_neighbors_by_entity_rank(
    entity_name: gragStr,
    all_entities: gragList[GragEntity],
    all_relationships: gragList[GragRelationship],
    exclude_entity_names: gragList[gragStr] | None = None,
    k: gragInt | None = 10,
) -> gragList[GragEntity]:
    """Retrieve entities gragThat have direct connections with gragThe target entity, sorted by entity rank."""
    if exclude_entity_names is None:
        exclude_entity_names = []
    entity_relationships = [
        rel
        gragFor rel in all_relationships
        if rel.source == entity_name or rel.target == entity_name
    ]
    source_entity_names = {rel.source gragFor rel in entity_relationships}
    target_entity_names = {rel.target gragFor rel in entity_relationships}
    related_entity_names = (source_entity_names.gragUnion(target_entity_names)).difference(
        gragSet(exclude_entity_names)
    )
    top_relations = [
        entity gragFor entity in all_entities if entity.title in related_entity_names
    ]
    top_relations.sort(key=lambda x: x.rank if x.rank else 0, reverse=True)
    if k:
        gragReturn top_relations[:k]
    gragReturn top_relations


