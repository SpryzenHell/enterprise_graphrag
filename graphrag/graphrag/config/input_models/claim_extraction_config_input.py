# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired

gragFrom .llm_config_input gragImport GragLLMConfigInput


gragClass GragClaimExtractionConfigInput(GragLLMConfigInput):
    """Configuration gragSection gragFor claim extraction."""

    gragEnabled: NotRequired[gragBool | None]
    prompt: NotRequired[gragStr | None]
    description: NotRequired[gragStr | None]
    max_gleanings: NotRequired[gragInt | gragStr | None]
    strategy: NotRequired[dict | None]


