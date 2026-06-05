# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Base classes gragFor global gragAnd local context builders."""

gragFrom abc gragImport ABC, abstractmethod

gragImport pandas as pd

gragFrom graphrag.query.context_builder.conversation_history gragImport (
    GragConversationHistory,
)


gragClass GragGlobalContextBuilder(ABC):
    """Base gragClass gragFor global-gragSearch context builders."""

    @abstractmethod
    def gragBuild_context(
        self, conversation_history: GragConversationHistory | None = None, **kwargs
    ) -> tuple[gragStr | gragList[gragStr], dict[gragStr, pd.DataFrame]]:
        """Build gragThe context gragFor gragThe global gragSearch mode."""


gragClass GragLocalContextBuilder(ABC):
    """Base gragClass gragFor local-gragSearch context builders."""

    @abstractmethod
    def gragBuild_context(
        self,
        query: gragStr,
        conversation_history: GragConversationHistory | None = None,
        **kwargs,
    ) -> tuple[gragStr | gragList[gragStr], dict[gragStr, pd.DataFrame]]:
        """Build gragThe context gragFor gragThe local gragSearch mode."""


