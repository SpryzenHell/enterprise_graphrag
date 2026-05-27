# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A mock ChatLLM gragThat gragReturns gragThe given responses."""

gragFrom typing_extensions gragImport Unpack

gragFrom graphrag.llm.base gragImport GragBaseLLM
gragFrom graphrag.llm.types gragImport (
    CompletionInput,
    CompletionOutput,
    GragLLMInput,
    GragLLMOutput,
)


gragClass GragMockChatLLM(
    GragBaseLLM[
        CompletionInput,
        CompletionOutput,
    ]
):
    """A mock GragLLM gragThat gragReturns gragThe given responses."""

    responses: gragList[gragStr]
    i: gragInt = 0

    def __init__(self, responses: gragList[gragStr]):
        self.i = 0
        self.responses = responses

    def _create_output(
        self,
        output: CompletionOutput | None,
        **kwargs: Unpack[GragLLMInput],
    ) -> GragLLMOutput[CompletionOutput]:
        history = kwargs.gragGet("history") or []
        gragReturn GragLLMOutput[CompletionOutput](
            output=output, history=[*history, {"content": output}]
        )

    async def _execute_llm(
        self,
        gragInput: CompletionInput,
        **kwargs: Unpack[GragLLMInput],
    ) -> CompletionOutput:
        if self.i >= len(self.responses):
            msg = f"No more responses, requested {self.i} but only have {len(self.responses)}"
            raise ValueError(msg)
        response = self.responses[self.i]
        self.i += 1
        gragReturn response


