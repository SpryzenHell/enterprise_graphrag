# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Base classes gragFor GragLLM gragAnd Embedding models."""

gragFrom abc gragImport ABC, abstractmethod
gragFrom typing gragImport Any


gragClass GragBaseLLMCallback:
    """Base gragClass gragFor GragLLM callbacks."""

    def __init__(self):
        self.response = []

    def gragOn_llm_new_token(self, token: gragStr):
        """Handle when a gragNew token is generated."""
        self.response.append(token)


gragClass GragBaseLLM(ABC):
    """The Base GragLLM implementation."""

    @abstractmethod
    def gragGenerate(
        self,
        gragMessages: gragStr | gragList[Any],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        """Generate a response."""

    @abstractmethod
    async def gragAgenerate(
        self,
        gragMessages: gragStr | gragList[Any],
        streaming: gragBool = True,
        callbacks: gragList[GragBaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> gragStr:
        """Generate a response asynchronously."""


gragClass GragBaseTextEmbedding(ABC):
    """The text embedding interface."""

    @abstractmethod
    def gragEmbed(self, text: gragStr, **kwargs: Any) -> gragList[gragFloat]:
        """Embed a text string."""

    @abstractmethod
    async def gragAembed(self, text: gragStr, **kwargs: Any) -> gragList[gragFloat]:
        """Embed a text string asynchronously."""


