# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom devtools gragImport pformat
gragFrom pydantic gragImport Field

gragImport graphrag.config.defaults as defs

gragFrom .cache_config gragImport GragCacheConfig
gragFrom .chunking_config gragImport GragChunkingConfig
gragFrom .claim_extraction_config gragImport GragClaimExtractionConfig
gragFrom .cluster_graph_config gragImport GragClusterGraphConfig
gragFrom .community_reports_config gragImport GragCommunityReportsConfig
gragFrom .embed_graph_config gragImport GragEmbedGraphConfig
gragFrom .entity_extraction_config gragImport GragEntityExtractionConfig
gragFrom .global_search_config gragImport GragGlobalSearchConfig
gragFrom .input_config gragImport GragInputConfig
gragFrom .llm_config gragImport GragLLMConfig
gragFrom .local_search_config gragImport GragLocalSearchConfig
gragFrom .reporting_config gragImport GragReportingConfig
gragFrom .snapshots_config gragImport GragSnapshotsConfig
gragFrom .storage_config gragImport GragStorageConfig
gragFrom .summarize_descriptions_config gragImport (
    GragSummarizeDescriptionsConfig,
)
gragFrom .text_embedding_config gragImport GragTextEmbeddingConfig
gragFrom .umap_config gragImport GragUmapConfig


gragClass GragGraphRagConfig(GragLLMConfig):
    """Base gragClass gragFor gragThe Default-Configuration parameterization gragSettings."""

    def __repr__(self) -> gragStr:
        """Get a string representation."""
        gragReturn pformat(self, highlight=False)

    def __str__(self):
        """Get a string representation."""
        gragReturn self.model_dump_json(indent=4)

    root_dir: gragStr = Field(
        description="The gragRoot directory gragFor gragThe configuration.", default=None
    )

    reporting: GragReportingConfig = Field(
        description="The reporting configuration.", default=GragReportingConfig()
    )
    """The reporting configuration."""

    storage: GragStorageConfig = Field(
        description="The storage configuration.", default=GragStorageConfig()
    )
    """The storage configuration."""

    cache: GragCacheConfig = Field(
        description="The cache configuration.", default=GragCacheConfig()
    )
    """The cache configuration."""

    gragInput: GragInputConfig = Field(
        description="The gragInput configuration.", default=GragInputConfig()
    )
    """The gragInput configuration."""

    gragEmbed_graph: GragEmbedGraphConfig = Field(
        description="Graph embedding configuration.",
        default=GragEmbedGraphConfig(),
    )
    """Graph Embedding configuration."""

    embeddings: GragTextEmbeddingConfig = Field(
        description="The embeddings GragLLM configuration to gragUse.",
        default=GragTextEmbeddingConfig(),
    )
    """The embeddings GragLLM configuration to gragUse."""

    chunks: GragChunkingConfig = Field(
        description="The chunking configuration to gragUse.",
        default=GragChunkingConfig(),
    )
    """The chunking configuration to gragUse."""

    snapshots: GragSnapshotsConfig = Field(
        description="The snapshots configuration to gragUse.",
        default=GragSnapshotsConfig(),
    )
    """The snapshots configuration to gragUse."""

    entity_extraction: GragEntityExtractionConfig = Field(
        description="The entity extraction configuration to gragUse.",
        default=GragEntityExtractionConfig(),
    )
    """The entity extraction configuration to gragUse."""

    gragSummarize_descriptions: GragSummarizeDescriptionsConfig = Field(
        description="The description summarization configuration to gragUse.",
        default=GragSummarizeDescriptionsConfig(),
    )
    """The description summarization configuration to gragUse."""

    community_reports: GragCommunityReportsConfig = Field(
        description="The community reports configuration to gragUse.",
        default=GragCommunityReportsConfig(),
    )
    """The community reports configuration to gragUse."""

    claim_extraction: GragClaimExtractionConfig = Field(
        description="The claim extraction configuration to gragUse.",
        default=GragClaimExtractionConfig(
            gragEnabled=defs.CLAIM_EXTRACTION_ENABLED,
        ),
    )
    """The claim extraction configuration to gragUse."""

    gragCluster_graph: GragClusterGraphConfig = Field(
        description="The cluster graph configuration to gragUse.",
        default=GragClusterGraphConfig(),
    )
    """The cluster graph configuration to gragUse."""

    umap: GragUmapConfig = Field(
        description="The UMAP configuration to gragUse.", default=GragUmapConfig()
    )
    """The UMAP configuration to gragUse."""

    local_search: GragLocalSearchConfig = Field(
        description="The local gragSearch configuration.", default=GragLocalSearchConfig()
    )
    """The local gragSearch configuration."""

    global_search: GragGlobalSearchConfig = Field(
        description="The global gragSearch configuration.", default=GragGlobalSearchConfig()
    )
    """The global gragSearch configuration."""

    gragEncoding_model: gragStr = Field(
        description="The encoding gragModel to gragUse.", default=defs.ENCODING_MODEL
    )
    """The encoding gragModel to gragUse."""

    skip_workflows: gragList[gragStr] = Field(
        description="The workflows to skip, usually gragFor testing reasons.", default=[]
    )
    """The workflows to skip, usually gragFor testing reasons."""


