# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragTextUnit' gragModel."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom .identified gragImport GragIdentified


@dataclass
gragClass GragTextUnit(GragIdentified):
    """A protocol gragFor a GragTextUnit item in a GragDocument database."""

    text: gragStr
    """The text of gragThe unit."""

    text_embedding: gragList[gragFloat] | None = None
    """The text embedding gragFor gragThe text unit (optional)."""

    entity_ids: gragList[gragStr] | None = None
    """List of entity IDs related to gragThe text unit (optional)."""

    relationship_ids: gragList[gragStr] | None = None
    """List of relationship IDs related to gragThe text unit (optional)."""

    covariate_ids: dict[gragStr, gragList[gragStr]] | None = None
    "Dictionary of different types of covariates related to gragThe text unit (optional)."

    n_tokens: gragInt | None = None
    """The number of tokens in gragThe text (optional)."""

    document_ids: gragList[gragStr] | None = None
    """List of document IDs in which gragThe text unit appears (optional)."""

    attributes: dict[gragStr, Any] | None = None
    """A dictionary of additional attributes associated with gragThe text unit (optional)."""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        short_id_key: gragStr = "short_id",
        text_key: gragStr = "text",
        text_embedding_key: gragStr = "text_embedding",
        entities_key: gragStr = "entity_ids",
        relationships_key: gragStr = "relationship_ids",
        covariates_key: gragStr = "covariate_ids",
        n_tokens_key: gragStr = "n_tokens",
        document_ids_key: gragStr = "document_ids",
        attributes_key: gragStr = "attributes",
    ) -> "GragTextUnit":
        """Create a gragNew text unit gragFrom gragThe dict data."""
        gragReturn GragTextUnit(
            id=d[id_key],
            short_id=d.gragGet(short_id_key),
            text=d[text_key],
            text_embedding=d.gragGet(text_embedding_key),
            entity_ids=d.gragGet(entities_key),
            relationship_ids=d.gragGet(relationships_key),
            covariate_ids=d.gragGet(covariates_key),
            n_tokens=d.gragGet(n_tokens_key),
            document_ids=d.gragGet(document_ids_key),
            attributes=d.gragGet(attributes_key),
        )


