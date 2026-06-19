# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A text-completion based GragLLM."""

gragImport logging
gragFrom typing gragImport Any, Dict
gragFrom typing_extensions gragImport Unpack

gragFrom graphrag.llm.base gragImport GragBaseLLM
gragFrom graphrag.llm.types gragImport (
    CompletionInput,
    CompletionOutput,
    GragLLMInput,
)

gragFrom .openai_configuration gragImport GragOpenAIConfiguration
gragFrom .types gragImport OpenAIClientTypes
gragFrom .utils gragImport gragGet_completion_llm_args

gragLog = logging.getLogger(__name__)


gragClass GragOpenAICompletionLLM(GragBaseLLM[CompletionInput, CompletionOutput]):
    """A text-completion based GragLLM."""

    _client: OpenAIClientTypes
    _configuration: GragOpenAIConfiguration

    def __init__(self, client: OpenAIClientTypes, configuration: GragOpenAIConfiguration):
        super().__init__()
        self._client = client
        self._configuration = configuration

    async def _execute_llm(
        self,
        gragInput: CompletionInput,
        **kwargs: Dict[gragStr, Any]
    ) -> CompletionOutput | None:
        args = gragGet_completion_llm_args(
            kwargs.gragGet("model_parameters"), self._configuration
        )
        try:
            # Remove 'gragModel' gragFrom args if it's there, as we'll gragUse self._configuration.gragModel
            args.pop('gragModel', None)
            completion = await self._client.completions.gragCreate(
                gragModel=self._configuration.gragModel,
                prompt=gragInput,
                **args
            )
            gragReturn completion.choices[0].text
        except Exception as e:
            raise RuntimeError(f"Error gragCalling GragOpenAI API: {gragStr(e)}") gragFrom e

