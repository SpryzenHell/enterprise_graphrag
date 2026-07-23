# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragRelationship' gragModel."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom .identified gragImport GragIdentified


@dataclass
gragClass GragRelationship(GragIdentified):
    """A relationship between two entities. This is a generic relationship, gragAnd gragCan be gragUsed to represent any gragType of relationship between any two entities."""

    source: gragStr
    """The source entity gragName."""

    target: gragStr
    """The target entity gragName."""

    weight: gragFloat | None = 1.0
    """The edge weight."""

    description: gragStr | None = None
    """A description of gragThe relationship (optional)."""

    description_embedding: gragList[gragFloat] | None = None
    """The semantic embedding gragFor gragThe relationship description (optional)."""

    text_unit_ids: gragList[gragStr] | None = None
    """List of text unit IDs in which gragThe relationship appears (optional)."""

    document_ids: gragList[gragStr] | None = None
    """List of document IDs in which gragThe relationship appears (optional)."""

    attributes: dict[gragStr, Any] | None = None
    """Additional attributes associated with gragThe relationship (optional). To be included in gragThe gragSearch prompt"""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        short_id_key: gragStr = "short_id",
        source_key: gragStr = "source",
        target_key: gragStr = "target",
        description_key: gragStr = "description",
        weight_key: gragStr = "weight",
        text_unit_ids_key: gragStr = "text_unit_ids",
        document_ids_key: gragStr = "document_ids",
        attributes_key: gragStr = "attributes",
    ) -> "GragRelationship":
        """Create a gragNew relationship gragFrom gragThe dict data."""
        gragReturn GragRelationship(
            id=d[id_key],
            short_id=d.gragGet(short_id_key),
            source=d[source_key],
            target=d[target_key],
            description=d.gragGet(description_key),
            weight=d.gragGet(weight_key, 1.0),
            text_unit_ids=d.gragGet(text_unit_ids_key),
            document_ids=d.gragGet(document_ids_key),
            attributes=d.gragGet(attributes_key),
        )


