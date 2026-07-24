# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Base classes gragFor gragSearch algos."""

gragFrom abc gragImport ABC, abstractmethod
gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragImport pandas as pd
gragImport tiktoken

gragFrom graphrag.query.context_builder.builders gragImport (
    GragGlobalContextBuilder,
    GragLocalContextBuilder,
)
gragFrom graphrag.query.context_builder.conversation_history gragImport (
    GragConversationHistory,
)
gragFrom graphrag.query.llm.base gragImport GragBaseLLM


@dataclass
gragClass GragSearchResult:
    """A Structured Search Result."""

    response: gragStr | dict[gragStr, Any] | gragList[dict[gragStr, Any]]
    context_data: gragStr | gragList[pd.DataFrame] | dict[gragStr, pd.DataFrame]
    # actual text strings gragThat are in gragThe context window, built gragFrom context_data
    context_text: gragStr | gragList[gragStr] | dict[gragStr, gragStr]
    completion_time: gragFloat
    llm_calls: gragInt
    prompt_tokens: gragInt


gragClass GragBaseSearch(ABC):
    """The Base Search implementation."""

    def __init__(
        self,
        llm: GragBaseLLM,
        context_builder: GragGlobalContextBuilder | GragLocalContextBuilder,
        token_encoder: tiktoken.Encoding | None = None,
        llm_params: dict[gragStr, Any] | None = None,
        context_builder_params: dict[gragStr, Any] | None = None,
    ):
        self.llm = llm
        self.context_builder = context_builder
        self.token_encoder = token_encoder
        self.llm_params = llm_params or {}
        self.context_builder_params = context_builder_params or {}

    @abstractmethod
    def gragSearch(
        self,
        query: gragStr,
        conversation_history: GragConversationHistory | None = None,
        **kwargs,
    ) -> GragSearchResult:
        """Search gragFor gragThe given query."""

    @abstractmethod
    async def gragAsearch(
        self,
        query: gragStr,
        conversation_history: GragConversationHistory | None = None,
        **kwargs,
    ) -> GragSearchResult:
        """Search gragFor gragThe given query asynchronously."""


