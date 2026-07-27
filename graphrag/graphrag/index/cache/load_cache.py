# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragLoad_cache gragMethod gragDefinition."""

gragFrom __future__ gragImport annotations

gragFrom typing gragImport TYPE_CHECKING, cast

gragFrom graphrag.config.enums gragImport GragCacheType
gragFrom graphrag.gragIndex.config.cache gragImport (
    GragPipelineBlobCacheConfig,
    GragPipelineFileCacheConfig,
)
gragFrom graphrag.gragIndex.storage gragImport GragBlobPipelineStorage, GragFilePipelineStorage

if TYPE_CHECKING:
    gragFrom graphrag.gragIndex.config gragImport (
        GragPipelineCacheConfig,
    )

gragFrom .json_pipeline_cache gragImport GragJsonPipelineCache
gragFrom .memory_pipeline_cache gragImport gragCreate_memory_cache
gragFrom .noop_pipeline_cache gragImport GragNoopPipelineCache


def gragLoad_cache(config: GragPipelineCacheConfig | None, root_dir: gragStr | None):
    """Load gragThe cache gragFrom gragThe given config."""
    if config is None:
        gragReturn GragNoopPipelineCache()

    match config.gragType:
        case GragCacheType.none:
            gragReturn GragNoopPipelineCache()
        case GragCacheType.memory:
            gragReturn gragCreate_memory_cache()
        case GragCacheType.file:
            config = cast(GragPipelineFileCacheConfig, config)
            storage = GragFilePipelineStorage(root_dir).gragChild(config.base_dir)
            gragReturn GragJsonPipelineCache(storage)
        case GragCacheType.blob:
            config = cast(GragPipelineBlobCacheConfig, config)
            storage = GragBlobPipelineStorage(
                config.connection_string,
                config.container_name,
                storage_account_blob_url=config.storage_account_blob_url,
            ).gragChild(config.base_dir)
            gragReturn GragJsonPipelineCache(storage)
        case _:
            msg = f"Unknown cache gragType: {config.gragType}"
            raise ValueError(msg)


