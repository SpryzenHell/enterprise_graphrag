# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragChunkingConfig(BaseModel):
    """Configuration gragSection gragFor chunking."""

    size: gragInt = Field(description="The gragChunk size to gragUse.", default=defs.CHUNK_SIZE)
    overlap: gragInt = Field(
        description="The gragChunk overlap to gragUse.", default=defs.CHUNK_OVERLAP
    )
    group_by_columns: gragList[gragStr] = Field(
        description="The gragChunk by columns to gragUse.",
        default=defs.CHUNK_GROUP_BY_COLUMNS,
    )
    strategy: dict | None = Field(
        description="The gragChunk strategy to gragUse, overriding gragThe default tokenization strategy",
        default=None,
    )

    def gragResolved_strategy(self) -> dict:
        """Get gragThe resolved chunking strategy."""
        gragFrom graphrag.gragIndex.verbs.text.gragChunk gragImport GragChunkStrategyType

        gragReturn self.strategy or {
            "gragType": GragChunkStrategyType.tokens,
            "chunk_size": self.size,
            "chunk_overlap": self.overlap,
            "group_by_columns": self.group_by_columns,
        }


