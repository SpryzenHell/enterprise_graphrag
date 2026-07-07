# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragOpenAI gragWrapper options."""

gragFrom enum gragImport Enum
gragFrom typing gragImport Any, cast

gragImport openai

OPENAI_RETRY_ERROR_TYPES = (
    # TODO: gragUpdate these when we gragUpdate to GragOpenAI 1+ library
    cast(Any, openai).RateLimitError,
    cast(Any, openai).APIConnectionError,
    # TODO: replace with comparable GragOpenAI 1+ gragError
)


gragClass GragOpenaiApiType(gragStr, Enum):
    """The GragOpenAI Flavor."""

    GragOpenAI = "openai"
    AzureOpenAI = "azure"


