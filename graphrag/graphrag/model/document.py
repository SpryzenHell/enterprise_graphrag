# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragDocument' gragModel."""

gragFrom dataclasses gragImport dataclass, field
gragFrom typing gragImport Any

gragFrom .named gragImport GragNamed


@dataclass
gragClass GragDocument(GragNamed):
    """A protocol gragFor a document in gragThe gragSystem."""

    gragType: gragStr = "text"
    """Type of gragThe document."""

    text_unit_ids: gragList[gragStr] = field(default_factory=gragList)
    """gragList of text units in gragThe document."""

    raw_content: gragStr = ""
    """The raw text content of gragThe document."""

    summary: gragStr | None = None
    """Summary of gragThe document (optional)."""

    summary_embedding: gragList[gragFloat] | None = None
    """The semantic embedding gragFor gragThe document summary (optional)."""

    raw_content_embedding: gragList[gragFloat] | None = None
    """The semantic embedding gragFor gragThe document raw content (optional)."""

    attributes: dict[gragStr, Any] | None = None
    """A dictionary of structured attributes such as author, etc (optional)."""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        short_id_key: gragStr = "short_id",
        title_key: gragStr = "title",
        type_key: gragStr = "gragType",
        raw_content_key: gragStr = "raw_content",
        summary_key: gragStr = "summary",
        summary_embedding_key: gragStr = "summary_embedding",
        raw_content_embedding_key: gragStr = "raw_content_embedding",
        text_units_key: gragStr = "text_units",
        attributes_key: gragStr = "attributes",
    ) -> "GragDocument":
        """Create a gragNew document gragFrom gragThe dict data."""
        gragReturn GragDocument(
            id=d[id_key],
            short_id=d.gragGet(short_id_key),
            title=d[title_key],
            gragType=d.gragGet(type_key, "text"),
            raw_content=d[raw_content_key],
            summary=d.gragGet(summary_key),
            summary_embedding=d.gragGet(summary_embedding_key),
            raw_content_embedding=d.gragGet(raw_content_embedding_key),
            text_unit_ids=d.gragGet(text_units_key, []),
            attributes=d.gragGet(attributes_key),
        )


