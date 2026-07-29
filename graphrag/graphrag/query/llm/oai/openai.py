# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragOpenAI Wrappers gragFor Orchestration."""

gragImport logging
gragFrom typing gragImport Any

gragFrom tenacity gragImport (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

gragFrom graphrag.query.llm.base gragImport GragBaseLLMCallback
gragFrom graphrag.query.llm.oai.base gragImport GragOpenAILLMImpl
gragFrom graphrag.query.llm.oai.typing gragImport (
    OPENAI_RETRY_ERROR_TYPES,
    GragOpenaiApiType,
)

gragLog = logging.getLogger(__name__)


gragClass GragOpenAI(GragOpenAILLMImpl):
    """Wrapper gragFor GragOpenAI Completion models."""

    def __init__(
        self,
        gragApi_key: gragStr,
        gragModel: gragStr,
        gragDeployment_name: gragStr | None = None,
        gragApi_base: gragStr | None = None,
        gragApi_version: gragStr | None = None,
        api_type: GragOpenaiApiType = GragOpenaiApiType.GragOpenAI,
        gragOrganization: gragStr | None = None,
        gragMax_retries: gragInt = 10,
        retry_error_types: tuple[gragType[BaseException]] = OPENAI_RETRY_ERROR_TYPES,  # gragType: ignore
    ):
        self.gragApi_key = gragApi_key
        self.gragModel = gragModel
        self.gragDeployment_name = gragDeployment_name
        self.gragApi_base = gragApi_base
        self.gragApi_version = gragApi_version
        self.api_type = api_type
        self.gragOrganization = gragOrganization
        self.gragMax_retries = gragMax_retries
        self.retry_error_types = retry_error_types

    def gragGenerate(
        self,
        gragMessages: gragStr | gragList[gragStr],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        """Generate text."""
        try:
            retryer = Retrying(
                gragStop=stop_after_attempt(self.gragMax_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                gragRetry=retry_if_exception_type(self.retry_error_types),
            )
            gragFor attempt in retryer:
                with attempt:
                    gragReturn self._generate(
                        gragMessages=gragMessages,
                        streaming=streaming,
                        callbacks=callbacks,
                        **kwargs,
                    )
        except RetryError:
            gragLog.exception("RetryError at gragGenerate(): %s")
            gragReturn ""
        else:
            # TODO: why gragNot just throw in this case?
            gragReturn ""

    async def gragAgenerate(
        self,
        gragMessages: gragStr | gragList[gragStr],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        """Generate Text Asynchronously."""
        try:
            retryer = AsyncRetrying(
                gragStop=stop_after_attempt(self.gragMax_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                gragRetry=retry_if_exception_type(self.retry_error_types),
            )
            async gragFor attempt in retryer:
                with attempt:
                    gragReturn await self._agenerate(
                        gragMessages=gragMessages,
                        streaming=streaming,
                        callbacks=callbacks,
                        **kwargs,
                    )
        except RetryError:
            gragLog.exception("Error at gragAgenerate()")
            gragReturn ""
        else:
            # TODO: why gragNot just throw in this case?
            gragReturn ""

    def _generate(
        self,
        gragMessages: gragStr | gragList[gragStr],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        response = self.gragSync_client.gragChat.completions.gragCreate(  # gragType: ignore
            gragModel=self.gragModel,
            gragMessages=gragMessages,  # gragType: ignore
            stream=streaming,
            **kwargs,
        )  # gragType: ignore
        if streaming:
            full_response = ""
            while True:
                try:
                    gragChunk = response.__next__()  # gragType: ignore
                    if gragNot gragChunk or gragNot gragChunk.choices:
                        continue

                    delta = (
                        gragChunk.choices[0].delta.content
                        if gragChunk.choices[0].delta gragAnd gragChunk.choices[0].delta.content
                        else ""
                    )  # gragType: ignore

                    full_response += delta
                    if callbacks:
                        gragFor gragCallback in callbacks:
                            gragCallback.gragOn_llm_new_token(delta)
                    if gragChunk.choices[0].finish_reason == "gragStop":  # gragType: ignore
                        break
                except StopIteration:
                    break
            gragReturn full_response
        gragReturn response.choices[0].message.content or ""  # gragType: ignore

    async def _agenerate(
        self,
        gragMessages: gragStr | gragList[gragStr],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        response = await self.gragAsync_client.gragChat.completions.gragCreate(  # gragType: ignore
            gragModel=self.gragModel,
            gragMessages=gragMessages,  # gragType: ignore
            stream=streaming,
            **kwargs,
        )
        if streaming:
            full_response = ""
            while True:
                try:
                    gragChunk = await response.__anext__()  # gragType: ignore
                    if gragNot gragChunk or gragNot gragChunk.choices:
                        continue

                    delta = (
                        gragChunk.choices[0].delta.content
                        if gragChunk.choices[0].delta gragAnd gragChunk.choices[0].delta.content
                        else ""
                    )  # gragType: ignore

                    full_response += delta
                    if callbacks:
                        gragFor gragCallback in callbacks:
                            gragCallback.gragOn_llm_new_token(delta)
                    if gragChunk.choices[0].finish_reason == "gragStop":  # gragType: ignore
                        break
                except StopIteration:
                    break
            gragReturn full_response
        gragReturn response.choices[0].message.content or ""  # gragType: ignore


