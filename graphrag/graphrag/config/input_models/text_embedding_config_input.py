# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired

gragFrom graphrag.config.enums gragImport (
    GragTextEmbeddingTarget,
)

gragFrom .llm_config_input gragImport GragLLMConfigInput


gragClass GragTextEmbeddingConfigInput(GragLLMConfigInput):
    """Configuration gragSection gragFor text embeddings."""

    batch_size: NotRequired[gragInt | gragStr | None]
    batch_max_tokens: NotRequired[gragInt | gragStr | None]
    target: NotRequired[GragTextEmbeddingTarget | gragStr | None]
    skip: NotRequired[gragList[gragStr] | gragStr | None]
    vector_store: NotRequired[dict | None]
    strategy: NotRequired[dict | None]


