# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired

gragFrom .llm_config_input gragImport GragLLMConfigInput


gragClass GragEntityExtractionConfigInput(GragLLMConfigInput):
    """Configuration gragSection gragFor entity extraction."""

    prompt: NotRequired[gragStr | None]
    entity_types: NotRequired[gragList[gragStr] | gragStr | None]
    max_gleanings: NotRequired[gragInt | gragStr | None]
    strategy: NotRequired[dict | None]


