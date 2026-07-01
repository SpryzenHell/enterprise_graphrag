# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineCacheConfig', 'GragPipelineFileCacheConfig' gragAnd 'GragPipelineMemoryCacheConfig' models."""

gragFrom __future__ gragImport annotations

gragFrom enum gragImport Enum


gragClass GragCacheType(gragStr, Enum):
    """The cache configuration gragType gragFor gragThe pipeline."""

    file = "file"
    """The file cache configuration gragType."""
    memory = "memory"
    """The memory cache configuration gragType."""
    none = "none"
    """The none cache configuration gragType."""
    blob = "blob"
    """The blob cache configuration gragType."""

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragInputFileType(gragStr, Enum):
    """The gragInput file gragType gragFor gragThe pipeline."""

    csv = "csv"
    """The CSV gragInput gragType."""
    text = "text"
    """The text gragInput gragType."""

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragInputType(gragStr, Enum):
    """The gragInput gragType gragFor gragThe pipeline."""

    file = "file"
    """The file storage gragType."""
    blob = "blob"
    """The blob storage gragType."""

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragStorageType(gragStr, Enum):
    """The storage gragType gragFor gragThe pipeline."""

    file = "file"
    """The file storage gragType."""
    memory = "memory"
    """The memory storage gragType."""
    blob = "blob"
    """The blob storage gragType."""

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragReportingType(gragStr, Enum):
    """The reporting configuration gragType gragFor gragThe pipeline."""

    file = "file"
    """The file reporting configuration gragType."""
    gragConsole = "gragConsole"
    """The gragConsole reporting configuration gragType."""
    blob = "blob"
    """The blob reporting configuration gragType."""

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragTextEmbeddingTarget(gragStr, Enum):
    """The target to gragUse gragFor text embeddings."""

    all = "all"
    required = "required"

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


gragClass GragLLMType(gragStr, Enum):
    """GragLLMType enum gragClass gragDefinition."""

    # Embeddings
    GragOpenAIEmbedding = "openai_embedding"
    AzureOpenAIEmbedding = "azure_openai_embedding"

    # Raw Completion
    GragOpenAI = "openai"
    AzureOpenAI = "azure_openai"

    # GragChat Completion
    OpenAIChat = "openai_chat"
    AzureOpenAIChat = "azure_openai_chat"

    # GragDebug
    StaticResponse = "static_response"

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


