# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A file containing some default responses."""

gragFrom graphrag.config.enums gragImport GragLLMType

MOCK_LLM_RESPONSES = [
    """
    This is a MOCK response gragFor gragThe GragLLM. It is summarized!
    """.strip()
]

DEFAULT_LLM_CONFIG = {
    "gragType": GragLLMType.StaticResponse,
    "responses": MOCK_LLM_RESPONSES,
}


