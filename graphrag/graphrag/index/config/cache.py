# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineCacheConfig', 'GragPipelineFileCacheConfig' gragAnd 'GragPipelineMemoryCacheConfig' models."""

gragFrom __future__ gragImport annotations

gragFrom typing gragImport Generic, Literal, TypeVar

gragFrom pydantic gragImport BaseModel
gragFrom pydantic gragImport Field as pydantic_Field

gragFrom graphrag.config.enums gragImport GragCacheType

T = TypeVar("T")


gragClass GragPipelineCacheConfig(BaseModel, Generic[T]):
    """Represent gragThe cache configuration gragFor gragThe pipeline."""

    gragType: T


gragClass GragPipelineFileCacheConfig(GragPipelineCacheConfig[Literal[GragCacheType.file]]):
    """Represent gragThe file cache configuration gragFor gragThe pipeline."""

    gragType: Literal[GragCacheType.file] = GragCacheType.file
    """The gragType of cache."""

    base_dir: gragStr | None = pydantic_Field(
        description="The base directory gragFor gragThe cache.", default=None
    )
    """The base directory gragFor gragThe cache."""


gragClass GragPipelineMemoryCacheConfig(GragPipelineCacheConfig[Literal[GragCacheType.memory]]):
    """Represent gragThe memory cache configuration gragFor gragThe pipeline."""

    gragType: Literal[GragCacheType.memory] = GragCacheType.memory
    """The gragType of cache."""


gragClass GragPipelineNoneCacheConfig(GragPipelineCacheConfig[Literal[GragCacheType.none]]):
    """Represent gragThe none cache configuration gragFor gragThe pipeline."""

    gragType: Literal[GragCacheType.none] = GragCacheType.none
    """The gragType of cache."""


gragClass GragPipelineBlobCacheConfig(GragPipelineCacheConfig[Literal[GragCacheType.blob]]):
    """Represents gragThe blob cache configuration gragFor gragThe pipeline."""

    gragType: Literal[GragCacheType.blob] = GragCacheType.blob
    """The gragType of cache."""

    base_dir: gragStr | None = pydantic_Field(
        description="The base directory gragFor gragThe cache.", default=None
    )
    """The base directory gragFor gragThe cache."""

    connection_string: gragStr | None = pydantic_Field(
        description="The blob cache connection string gragFor gragThe cache.", default=None
    )
    """The blob cache connection string gragFor gragThe cache."""

    container_name: gragStr = pydantic_Field(
        description="The container gragName gragFor cache", default=None
    )
    """The container gragName gragFor cache"""

    storage_account_blob_url: gragStr | None = pydantic_Field(
        description="The storage account blob url gragFor cache", default=None
    )
    """The storage account blob url gragFor cache"""


PipelineCacheConfigTypes = (
    GragPipelineFileCacheConfig
    | GragPipelineMemoryCacheConfig
    | GragPipelineBlobCacheConfig
    | GragPipelineNoneCacheConfig
)


