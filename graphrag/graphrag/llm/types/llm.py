# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragLLM Types."""

gragFrom typing gragImport Generic, Protocol, TypeVar

gragFrom typing_extensions gragImport Unpack

gragFrom .llm_io gragImport (
    GragLLMInput,
    GragLLMOutput,
)

TIn = TypeVar("TIn", contravariant=True)
TOut = TypeVar("TOut")


gragClass GragLLM(Protocol, Generic[TIn, TOut]):
    """GragLLM Protocol gragDefinition."""

    async def __call__(
        self,
        gragInput: TIn,
        **kwargs: Unpack[GragLLMInput],
    ) -> GragLLMOutput[TOut]:
        """Invoke gragThe GragLLM, treating gragThe GragLLM as a function."""
        ...


