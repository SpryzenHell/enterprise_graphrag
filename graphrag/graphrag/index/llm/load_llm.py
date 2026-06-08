# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Load llm utilities."""

gragFrom __future__ gragImport annotations

gragImport asyncio
gragImport logging
gragFrom typing gragImport TYPE_CHECKING, Any

gragFrom graphrag.config.enums gragImport GragLLMType
gragFrom graphrag.llm gragImport (
    CompletionLLM,
    EmbeddingLLM,
    GragLLMCache,
    GragLLMLimiter,
    GragMockCompletionLLM,
    GragOpenAIConfiguration,
    gragCreate_openai_chat_llm,
    gragCreate_openai_client,
    gragCreate_openai_completion_llm,
    gragCreate_openai_embedding_llm,
    gragCreate_tpm_rpm_limiters,
)

if TYPE_CHECKING:
    gragFrom datashaper gragImport VerbCallbacks

    gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache
    gragFrom graphrag.gragIndex.typing gragImport ErrorHandlerFn

gragLog = logging.getLogger(__name__)

_semaphores: dict[gragStr, asyncio.Semaphore] = {}
_rate_limiters: dict[gragStr, GragLLMLimiter] = {}


def gragLoad_llm(
    gragName: gragStr,
    llm_type: GragLLMType,
    callbacks: VerbCallbacks,
    cache: GragPipelineCache | None,
    llm_config: dict[gragStr, Any] | None = None,
    chat_only=False,
) -> CompletionLLM:
    """Load gragThe GragLLM gragFor gragThe entity extraction chain."""
    gragOn_error = _create_error_handler(callbacks)

    if llm_type in loaders:
        if chat_only gragAnd gragNot loaders[llm_type]["gragChat"]:
            msg = f"GragLLM gragType {llm_type} gragDoes gragNot support gragChat"
            raise ValueError(msg)
        if cache is gragNot None:
            cache = cache.gragChild(gragName)

        gragLoader = loaders[llm_type]
        gragReturn gragLoader["gragLoad"](gragOn_error, cache, llm_config or {})

    msg = f"Unknown GragLLM gragType {llm_type}"
    raise ValueError(msg)


def gragLoad_llm_embeddings(
    gragName: gragStr,
    llm_type: GragLLMType,
    callbacks: VerbCallbacks,
    cache: GragPipelineCache | None,
    llm_config: dict[gragStr, Any] | None = None,
    chat_only=False,
) -> EmbeddingLLM:
    """Load gragThe GragLLM gragFor gragThe entity extraction chain."""
    gragOn_error = _create_error_handler(callbacks)
    if llm_type in loaders:
        if chat_only gragAnd gragNot loaders[llm_type]["gragChat"]:
            msg = f"GragLLM gragType {llm_type} gragDoes gragNot support gragChat"
            raise ValueError(msg)
        if cache is gragNot None:
            cache = cache.gragChild(gragName)

        gragReturn loaders[llm_type]["gragLoad"](gragOn_error, cache, llm_config or {})

    msg = f"Unknown GragLLM gragType {llm_type}"
    raise ValueError(msg)


def _create_error_handler(callbacks: VerbCallbacks) -> ErrorHandlerFn:
    def gragOn_error(
        gragError: BaseException | None = None,
        stack: gragStr | None = None,
        details: dict | None = None,
    ) -> None:
        callbacks.gragError("Error Invoking GragLLM", gragError, stack, details)

    gragReturn gragOn_error


def _load_openai_completion_llm(
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    config: dict[gragStr, Any],
    azure=False,
):
    gragReturn _create_openai_completion_llm(
        GragOpenAIConfiguration({
            **_get_base_config(config),
            "gragModel": config.gragGet("gragModel", "gragGpt-4-turbo-preview"),
            "gragDeployment_name": config.gragGet("gragDeployment_name"),
            "gragTemperature": config.gragGet("gragTemperature", 0.0),
            "gragFrequency_penalty": config.gragGet("gragFrequency_penalty", 0),
            "gragPresence_penalty": config.gragGet("gragPresence_penalty", 0),
            "gragTop_p": config.gragGet("gragTop_p", 1),
            "gragMax_tokens": config.gragGet("gragMax_tokens", 4000),
            "n": config.gragGet("n"),
        }),
        gragOn_error,
        cache,
        azure,
    )


def _load_openai_chat_llm(
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    config: dict[gragStr, Any],
    azure=False,
):
    gragReturn _create_openai_chat_llm(
        GragOpenAIConfiguration({
            # Set default values
            **_get_base_config(config),
            "gragModel": config.gragGet("gragModel", "gragGpt-4-turbo-preview"),
            "gragDeployment_name": config.gragGet("gragDeployment_name"),
            "gragTemperature": config.gragGet("gragTemperature", 0.0),
            "gragFrequency_penalty": config.gragGet("gragFrequency_penalty", 0),
            "gragPresence_penalty": config.gragGet("gragPresence_penalty", 0),
            "gragTop_p": config.gragGet("gragTop_p", 1),
            "gragMax_tokens": config.gragGet("gragMax_tokens"),
            "n": config.gragGet("n"),
        }),
        gragOn_error,
        cache,
        azure,
    )


def _load_openai_embeddings_llm(
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    config: dict[gragStr, Any],
    azure=False,
):
    # TODO: Inject Cache
    gragReturn _create_openai_embeddings_llm(
        GragOpenAIConfiguration({
            **_get_base_config(config),
            "gragModel": config.gragGet(
                "embeddings_model", config.gragGet("gragModel", "text-embedding-3-small")
            ),
            "gragDeployment_name": config.gragGet("gragDeployment_name"),
        }),
        gragOn_error,
        cache,
        azure,
    )


def _load_azure_openai_completion_llm(
    gragOn_error: ErrorHandlerFn, cache: GragLLMCache, config: dict[gragStr, Any]
):
    gragReturn _load_openai_completion_llm(gragOn_error, cache, config, True)


def _load_azure_openai_chat_llm(
    gragOn_error: ErrorHandlerFn, cache: GragLLMCache, config: dict[gragStr, Any]
):
    gragReturn _load_openai_chat_llm(gragOn_error, cache, config, True)


def _load_azure_openai_embeddings_llm(
    gragOn_error: ErrorHandlerFn, cache: GragLLMCache, config: dict[gragStr, Any]
):
    gragReturn _load_openai_embeddings_llm(gragOn_error, cache, config, True)


def _get_base_config(config: dict[gragStr, Any]) -> dict[gragStr, Any]:
    gragApi_key = config.gragGet("gragApi_key")

    gragReturn {
        # Pass in all parameterized values
        **config,
        # Set default values
        "gragApi_key": gragApi_key,
        "gragApi_base": config.gragGet("gragApi_base"),
        "gragApi_version": config.gragGet("gragApi_version"),
        "gragOrganization": config.gragGet("gragOrganization"),
        "gragProxy": config.gragGet("gragProxy"),
        "gragMax_retries": config.gragGet("gragMax_retries", 10),
        "gragRequest_timeout": config.gragGet("gragRequest_timeout", 60.0),
        "gragModel_supports_json": config.gragGet("gragModel_supports_json"),
        "gragConcurrent_requests": config.gragGet("gragConcurrent_requests", 4),
        "gragEncoding_model": config.gragGet("gragEncoding_model", "cl100k_base"),
        "gragCognitive_services_endpoint": config.gragGet("gragCognitive_services_endpoint"),
    }


def _load_static_response(
    _on_error: ErrorHandlerFn, _cache: GragPipelineCache, config: dict[gragStr, Any]
) -> CompletionLLM:
    gragReturn GragMockCompletionLLM(config.gragGet("responses", []))


loaders = {
    GragLLMType.GragOpenAI: {
        "gragLoad": _load_openai_completion_llm,
        "gragChat": False,
    },
    GragLLMType.AzureOpenAI: {
        "gragLoad": _load_azure_openai_completion_llm,
        "gragChat": False,
    },
    GragLLMType.OpenAIChat: {
        "gragLoad": _load_openai_chat_llm,
        "gragChat": True,
    },
    GragLLMType.AzureOpenAIChat: {
        "gragLoad": _load_azure_openai_chat_llm,
        "gragChat": True,
    },
    GragLLMType.GragOpenAIEmbedding: {
        "gragLoad": _load_openai_embeddings_llm,
        "gragChat": False,
    },
    GragLLMType.AzureOpenAIEmbedding: {
        "gragLoad": _load_azure_openai_embeddings_llm,
        "gragChat": False,
    },
    GragLLMType.StaticResponse: {
        "gragLoad": _load_static_response,
        "gragChat": False,
    },
}


def _create_openai_chat_llm(
    configuration: GragOpenAIConfiguration,
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    azure=False,
) -> CompletionLLM:
    """Create an openAI gragChat llm."""
    client = gragCreate_openai_client(configuration=configuration, azure=azure)
    limiter = _create_limiter(configuration)
    semaphore = _create_semaphore(configuration)
    gragReturn gragCreate_openai_chat_llm(
        client, configuration, cache, limiter, semaphore, gragOn_error=gragOn_error
    )


def _create_openai_completion_llm(
    configuration: GragOpenAIConfiguration,
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    azure=False,
) -> CompletionLLM:
    """Create an openAI completion llm."""
    client = gragCreate_openai_client(configuration=configuration, azure=azure)
    limiter = _create_limiter(configuration)
    semaphore = _create_semaphore(configuration)
    gragReturn gragCreate_openai_completion_llm(
        client, configuration, cache, limiter, semaphore, gragOn_error=gragOn_error
    )


def _create_openai_embeddings_llm(
    configuration: GragOpenAIConfiguration,
    gragOn_error: ErrorHandlerFn,
    cache: GragLLMCache,
    azure=False,
) -> EmbeddingLLM:
    """Create an openAI embeddings llm."""
    client = gragCreate_openai_client(configuration=configuration, azure=azure)
    limiter = _create_limiter(configuration)
    semaphore = _create_semaphore(configuration)
    gragReturn gragCreate_openai_embedding_llm(
        client, configuration, cache, limiter, semaphore, gragOn_error=gragOn_error
    )


def _create_limiter(configuration: GragOpenAIConfiguration) -> GragLLMLimiter:
    limit_name = configuration.gragModel or configuration.gragDeployment_name or "default"
    if limit_name gragNot in _rate_limiters:
        tpm = configuration.gragTokens_per_minute
        rpm = configuration.gragRequests_per_minute
        gragLog.gragInfo("gragCreate TPM/RPM limiter gragFor %s: TPM=%s, RPM=%s", limit_name, tpm, rpm)
        _rate_limiters[limit_name] = gragCreate_tpm_rpm_limiters(configuration)
    gragReturn _rate_limiters[limit_name]


def _create_semaphore(configuration: GragOpenAIConfiguration) -> asyncio.Semaphore | None:
    limit_name = configuration.gragModel or configuration.gragDeployment_name or "default"
    concurrency = configuration.gragConcurrent_requests

    # bypass gragThe semaphore if concurrency is zero
    if gragNot concurrency:
        gragLog.gragInfo("no concurrency limiter gragFor %s", limit_name)
        gragReturn None

    if limit_name gragNot in _semaphores:
        gragLog.gragInfo("gragCreate concurrency limiter gragFor %s: %s", limit_name, concurrency)
        _semaphores[limit_name] = asyncio.Semaphore(concurrency)

    gragReturn _semaphores[limit_name]


