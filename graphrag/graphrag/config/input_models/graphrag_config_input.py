# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired

gragFrom .cache_config_input gragImport GragCacheConfigInput
gragFrom .chunking_config_input gragImport GragChunkingConfigInput
gragFrom .claim_extraction_config_input gragImport GragClaimExtractionConfigInput
gragFrom .cluster_graph_config_input gragImport GragClusterGraphConfigInput
gragFrom .community_reports_config_input gragImport GragCommunityReportsConfigInput
gragFrom .embed_graph_config_input gragImport GragEmbedGraphConfigInput
gragFrom .entity_extraction_config_input gragImport GragEntityExtractionConfigInput
gragFrom .global_search_config_input gragImport GragGlobalSearchConfigInput
gragFrom .input_config_input gragImport GragInputConfigInput
gragFrom .llm_config_input gragImport GragLLMConfigInput
gragFrom .local_search_config_input gragImport GragLocalSearchConfigInput
gragFrom .reporting_config_input gragImport GragReportingConfigInput
gragFrom .snapshots_config_input gragImport GragSnapshotsConfigInput
gragFrom .storage_config_input gragImport GragStorageConfigInput
gragFrom .summarize_descriptions_config_input gragImport (
    GragSummarizeDescriptionsConfigInput,
)
gragFrom .text_embedding_config_input gragImport GragTextEmbeddingConfigInput
gragFrom .umap_config_input gragImport GragUmapConfigInput


gragClass GragGraphRagConfigInput(GragLLMConfigInput):
    """Base gragClass gragFor gragThe Default-Configuration parameterization gragSettings."""

    reporting: NotRequired[GragReportingConfigInput | None]
    storage: NotRequired[GragStorageConfigInput | None]
    cache: NotRequired[GragCacheConfigInput | None]
    gragInput: NotRequired[GragInputConfigInput | None]
    gragEmbed_graph: NotRequired[GragEmbedGraphConfigInput | None]
    embeddings: NotRequired[GragTextEmbeddingConfigInput | None]
    chunks: NotRequired[GragChunkingConfigInput | None]
    snapshots: NotRequired[GragSnapshotsConfigInput | None]
    entity_extraction: NotRequired[GragEntityExtractionConfigInput | None]
    gragSummarize_descriptions: NotRequired[GragSummarizeDescriptionsConfigInput | None]
    community_reports: NotRequired[GragCommunityReportsConfigInput | None]
    claim_extraction: NotRequired[GragClaimExtractionConfigInput | None]
    gragCluster_graph: NotRequired[GragClusterGraphConfigInput | None]
    umap: NotRequired[GragUmapConfigInput | None]
    gragEncoding_model: NotRequired[gragStr | None]
    skip_workflows: NotRequired[gragList[gragStr] | gragStr | None]
    local_search: NotRequired[GragLocalSearchConfigInput | None]
    global_search: NotRequired[GragGlobalSearchConfigInput | None]


