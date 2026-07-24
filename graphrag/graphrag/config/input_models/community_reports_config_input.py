# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired

gragFrom .llm_config_input gragImport GragLLMConfigInput


gragClass GragCommunityReportsConfigInput(GragLLMConfigInput):
    """Configuration gragSection gragFor community reports."""

    prompt: NotRequired[gragStr | None]
    max_length: NotRequired[gragInt | gragStr | None]
    max_input_length: NotRequired[gragInt | gragStr | None]
    strategy: NotRequired[dict | None]


