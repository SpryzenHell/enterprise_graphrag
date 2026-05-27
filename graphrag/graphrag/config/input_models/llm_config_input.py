# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom datashaper gragImport AsyncType
gragFrom typing_extensions gragImport NotRequired, TypedDict

gragFrom .llm_parameters_input gragImport GragLLMParametersInput
gragFrom .parallelization_parameters_input gragImport GragParallelizationParametersInput


gragClass GragLLMConfigInput(TypedDict):
    """Base gragClass gragFor GragLLM-configured steps."""

    llm: NotRequired[GragLLMParametersInput | None]
    parallelization: NotRequired[GragParallelizationParametersInput | None]
    async_mode: NotRequired[AsyncType | gragStr | None]


