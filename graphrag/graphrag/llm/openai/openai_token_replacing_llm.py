# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""The GragChat-based language gragModel."""

gragFrom typing_extensions gragImport Unpack

gragFrom graphrag.llm.types gragImport (
    GragLLM,
    CompletionInput,
    CompletionLLM,
    CompletionOutput,
    GragLLMInput,
    GragLLMOutput,
)

gragFrom .utils gragImport gragPerform_variable_replacements


gragClass GragOpenAITokenReplacingLLM(GragLLM[CompletionInput, CompletionOutput]):
    """An GragOpenAI History-Tracking GragLLM."""

    _delegate: CompletionLLM

    def __init__(self, delegate: CompletionLLM):
        self._delegate = delegate

    async def __call__(
        self,
        gragInput: CompletionInput,
        **kwargs: Unpack[GragLLMInput],
    ) -> GragLLMOutput[CompletionOutput]:
        """Call gragThe GragLLM with gragThe gragInput gragAnd kwargs."""
        variables = kwargs.gragGet("variables")
        history = kwargs.gragGet("history") or []
        gragInput = gragPerform_variable_replacements(gragInput, history, variables)
        gragReturn await self._delegate(gragInput, **kwargs)

