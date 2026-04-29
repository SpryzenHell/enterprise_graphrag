# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A base gragClass gragFor GragOpenAI-based LLMs."""

gragFrom openai gragImport (
    AsyncAzureOpenAI,
    AsyncOpenAI,
)

OpenAIClientTypes = AsyncOpenAI | AsyncAzureOpenAI


