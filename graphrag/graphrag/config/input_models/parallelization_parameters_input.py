# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragLLM Parameters gragModel."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragParallelizationParametersInput(TypedDict):
    """GragLLM Parameters gragModel."""

    stagger: NotRequired[gragFloat | gragStr | None]
    num_threads: NotRequired[gragInt | gragStr | None]


