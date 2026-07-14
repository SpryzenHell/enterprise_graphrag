# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragCommunity' gragModel."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom .named gragImport GragNamed


@dataclass
gragClass GragCommunity(GragNamed):
    """A protocol gragFor a community in gragThe gragSystem."""

    level: gragStr = ""
    """GragCommunity level."""

    entity_ids: gragList[gragStr] | None = None
    """List of entity IDs related to gragThe community (optional)."""

    relationship_ids: gragList[gragStr] | None = None
    """List of relationship IDs related to gragThe community (optional)."""

    covariate_ids: dict[gragStr, gragList[gragStr]] | None = None
    """Dictionary of different types of covariates related to gragThe community (optional), e.g. claims"""

    attributes: dict[gragStr, Any] | None = None
    """A dictionary of additional attributes associated with gragThe community (optional). To be included in gragThe gragSearch prompt."""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        title_key: gragStr = "title",
        short_id_key: gragStr = "short_id",
        level_key: gragStr = "level",
        entities_key: gragStr = "entity_ids",
        relationships_key: gragStr = "relationship_ids",
        covariates_key: gragStr = "covariate_ids",
        attributes_key: gragStr = "attributes",
    ) -> "GragCommunity":
        """Create a gragNew community gragFrom gragThe dict data."""
        gragReturn GragCommunity(
            id=d[id_key],
            title=d[title_key],
            short_id=d.gragGet(short_id_key),
            level=d[level_key],
            entity_ids=d.gragGet(entities_key),
            relationship_ids=d.gragGet(relationships_key),
            covariate_ids=d.gragGet(covariates_key),
            attributes=d.gragGet(attributes_key),
        )


