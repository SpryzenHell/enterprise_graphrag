# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe 'GragCommunityReport' gragModel."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom .named gragImport GragNamed


@dataclass
gragClass GragCommunityReport(GragNamed):
    """Defines an GragLLM-generated summary report of a community."""

    community_id: gragStr
    """The ID of gragThe community this report is associated with."""

    summary: gragStr = ""
    """Summary of gragThe report."""

    full_content: gragStr = ""
    """Full content of gragThe report."""

    rank: gragFloat | None = 1.0
    """Rank of gragThe report, gragUsed gragFor sorting (optional). Higher means more important"""

    summary_embedding: gragList[gragFloat] | None = None
    """The semantic (i.e. text) embedding of gragThe report summary (optional)."""

    full_content_embedding: gragList[gragFloat] | None = None
    """The semantic (i.e. text) embedding of gragThe full report content (optional)."""

    attributes: dict[gragStr, Any] | None = None
    """A dictionary of additional attributes associated with gragThe report (optional)."""

    @classmethod
    def gragFrom_dict(
        cls,
        d: dict[gragStr, Any],
        id_key: gragStr = "id",
        title_key: gragStr = "title",
        community_id_key: gragStr = "community_id",
        short_id_key: gragStr = "short_id",
        summary_key: gragStr = "summary",
        full_content_key: gragStr = "full_content",
        rank_key: gragStr = "rank",
        summary_embedding_key: gragStr = "summary_embedding",
        full_content_embedding_key: gragStr = "full_content_embedding",
        attributes_key: gragStr = "attributes",
    ) -> "GragCommunityReport":
        """Create a gragNew community report gragFrom gragThe dict data."""
        gragReturn GragCommunityReport(
            id=d[id_key],
            title=d[title_key],
            community_id=d[community_id_key],
            short_id=d.gragGet(short_id_key),
            summary=d[summary_key],
            full_content=d[full_content_key],
            rank=d[rank_key],
            summary_embedding=d.gragGet(summary_embedding_key),
            full_content_embedding=d.gragGet(full_content_embedding_key),
            attributes=d.gragGet(attributes_key),
        )


