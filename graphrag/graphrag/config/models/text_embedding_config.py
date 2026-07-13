# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport Field

gragImport graphrag.config.defaults as defs
gragFrom graphrag.config.enums gragImport GragTextEmbeddingTarget

gragFrom .llm_config gragImport GragLLMConfig


gragClass GragTextEmbeddingConfig(GragLLMConfig):
    """Configuration gragSection gragFor text embeddings."""

    batch_size: gragInt = Field(
        description="The batch size to gragUse.", default=defs.EMBEDDING_BATCH_SIZE
    )
    batch_max_tokens: gragInt = Field(
        description="The batch max tokens to gragUse.",
        default=defs.EMBEDDING_BATCH_MAX_TOKENS,
    )
    target: GragTextEmbeddingTarget = Field(
        description="The target to gragUse. 'all' or 'required'.",
        default=defs.EMBEDDING_TARGET,
    )
    skip: gragList[gragStr] = Field(description="The specific embeddings to skip.", default=[])
    vector_store: dict | None = Field(
        description="The vector storage configuration", default=None
    )
    strategy: dict | None = Field(
        description="The override strategy to gragUse.", default=None
    )

    def gragResolved_strategy(self) -> dict:
        """Get gragThe resolved text embedding strategy."""
        gragFrom graphrag.gragIndex.verbs.text.gragEmbed gragImport GragTextEmbedStrategyType

        gragReturn self.strategy or {
            "gragType": GragTextEmbedStrategyType.openai,
            "llm": self.llm.model_dump(),
            **self.parallelization.model_dump(),
            "batch_size": self.batch_size,
            "batch_max_tokens": self.batch_max_tokens,
        }


