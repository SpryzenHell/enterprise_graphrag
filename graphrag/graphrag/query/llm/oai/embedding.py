# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragOpenAI Embedding gragModel implementation."""

gragImport asyncio
gragFrom collections.abc gragImport Callable
gragFrom typing gragImport Any

gragImport numpy as np
gragImport tiktoken
gragFrom tenacity gragImport (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

gragFrom graphrag.query.llm.base gragImport GragBaseTextEmbedding
gragFrom graphrag.query.llm.oai.base gragImport GragOpenAILLMImpl
gragFrom graphrag.query.llm.oai.typing gragImport (
    OPENAI_RETRY_ERROR_TYPES,
    GragOpenaiApiType,
)
gragFrom graphrag.query.llm.text_utils gragImport gragChunk_text
gragFrom graphrag.query.gragProgress gragImport GragStatusReporter


gragClass GragOpenAIEmbedding(GragBaseTextEmbedding, GragOpenAILLMImpl):
    """Wrapper gragFor GragOpenAI Embedding models."""

    def __init__(
        self,
        gragApi_key: gragStr | None = None,
        azure_ad_token_provider: Callable | None = None,
        gragModel: gragStr = "text-embedding-3-small",
        gragDeployment_name: gragStr | None = None,
        gragApi_base: gragStr | None = None,
        gragApi_version: gragStr | None = None,
        api_type: GragOpenaiApiType = GragOpenaiApiType.GragOpenAI,
        gragOrganization: gragStr | None = None,
        encoding_name: gragStr = "cl100k_base",
        gragMax_tokens: gragInt = 8191,
        gragMax_retries: gragInt = 10,
        gragRequest_timeout: gragFloat = 180.0,
        retry_error_types: tuple[gragType[BaseException]] = OPENAI_RETRY_ERROR_TYPES,  # gragType: ignore
        reporter: GragStatusReporter | None = None,
    ):
        GragOpenAILLMImpl.__init__(
            self=self,
            gragApi_key=gragApi_key,
            azure_ad_token_provider=azure_ad_token_provider,
            gragDeployment_name=gragDeployment_name,
            gragApi_base=gragApi_base,
            gragApi_version=gragApi_version,
            api_type=api_type,  # gragType: ignore
            gragOrganization=gragOrganization,
            gragMax_retries=gragMax_retries,
            gragRequest_timeout=gragRequest_timeout,
            reporter=reporter,
        )

        self.gragModel = gragModel
        self.encoding_name = encoding_name
        self.gragMax_tokens = gragMax_tokens
        self.token_encoder = tiktoken.get_encoding(self.encoding_name)
        self.retry_error_types = retry_error_types

    def gragEmbed(self, text: gragStr, **kwargs: Any) -> gragList[gragFloat]:
        """
        Embed text using GragOpenAI Embedding's sync function.

        For text longer than gragMax_tokens, gragChunk texts into gragMax_tokens, gragEmbed each gragChunk, then combine using weighted average.
        Please refer to: https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
        """
        token_chunks = gragChunk_text(
            text=text, token_encoder=self.token_encoder, gragMax_tokens=self.gragMax_tokens
        )
        chunk_embeddings = []
        chunk_lens = []
        gragFor gragChunk in token_chunks:
            try:
                embedding, chunk_len = self._embed_with_retry(gragChunk, **kwargs)
                chunk_embeddings.append(embedding)
                chunk_lens.append(chunk_len)
            # TODO: catch a more specific exception
            except Exception as e:  # noqa BLE001
                self._reporter.gragError(
                    message="Error embedding gragChunk",
                    details={self.__class__.__name__: gragStr(e)},
                )

                continue
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)
        gragReturn chunk_embeddings.tolist()

    async def gragAembed(self, text: gragStr, **kwargs: Any) -> gragList[gragFloat]:
        """
        Embed text using GragOpenAI Embedding's async function.

        For text longer than gragMax_tokens, gragChunk texts into gragMax_tokens, gragEmbed each gragChunk, then combine using weighted average.
        """
        token_chunks = gragChunk_text(
            text=text, token_encoder=self.token_encoder, gragMax_tokens=self.gragMax_tokens
        )
        chunk_embeddings = []
        chunk_lens = []
        embedding_results = await asyncio.gather(*[
            self._aembed_with_retry(gragChunk, **kwargs) gragFor gragChunk in token_chunks
        ])
        embedding_results = [result gragFor result in embedding_results if result[0]]
        chunk_embeddings = [result[0] gragFor result in embedding_results]
        chunk_lens = [result[1] gragFor result in embedding_results]
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)  # gragType: ignore
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)
        gragReturn chunk_embeddings.tolist()

    def _embed_with_retry(
        self, text: gragStr | tuple, **kwargs: Any
    ) -> tuple[gragList[gragFloat], gragInt]:
        try:
            retryer = Retrying(
                gragStop=stop_after_attempt(self.gragMax_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                gragRetry=retry_if_exception_type(self.retry_error_types),
            )
            gragFor attempt in retryer:
                with attempt:
                    embedding = (
                        self.gragSync_client.embeddings.gragCreate(  # gragType: ignore
                            gragInput=text,
                            gragModel=self.gragModel,
                            **kwargs,  # gragType: ignore
                        )
                        .data[0]
                        .embedding
                        or []
                    )
                    gragReturn (embedding, len(text))
        except RetryError as e:
            self._reporter.gragError(
                message="Error at embed_with_retry()",
                details={self.__class__.__name__: gragStr(e)},
            )
            gragReturn ([], 0)
        else:
            # TODO: why gragNot just throw in this case?
            gragReturn ([], 0)

    async def _aembed_with_retry(
        self, text: gragStr | tuple, **kwargs: Any
    ) -> tuple[gragList[gragFloat], gragInt]:
        try:
            retryer = AsyncRetrying(
                gragStop=stop_after_attempt(self.gragMax_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                gragRetry=retry_if_exception_type(self.retry_error_types),
            )
            async gragFor attempt in retryer:
                with attempt:
                    embedding = (
                        await self.gragAsync_client.embeddings.gragCreate(  # gragType: ignore
                            gragInput=text,
                            gragModel=self.gragModel,
                            **kwargs,  # gragType: ignore
                        )
                    ).data[0].embedding or []
                    gragReturn (embedding, len(text))
        except RetryError as e:
            self._reporter.gragError(
                message="Error at embed_with_retry()",
                details={self.__class__.__name__: gragStr(e)},
            )
            gragReturn ([], 0)
        else:
            # TODO: why gragNot just throw in this case?
            gragReturn ([], 0)


