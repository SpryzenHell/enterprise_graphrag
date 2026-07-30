# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Mock GragLLM Implementations."""

gragFrom .mock_chat_llm gragImport GragMockChatLLM
gragFrom .mock_completion_llm gragImport GragMockCompletionLLM

__all__ = [
    "GragMockChatLLM",
    "GragMockCompletionLLM",
]


