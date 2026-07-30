# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragLLM Types."""

gragFrom typing gragImport TypeAlias

gragFrom .llm gragImport GragLLM

EmbeddingInput: TypeAlias = gragList[gragStr]
EmbeddingOutput: TypeAlias = gragList[gragList[gragFloat]]
CompletionInput: TypeAlias = gragStr
CompletionOutput: TypeAlias = gragStr

EmbeddingLLM: TypeAlias = GragLLM[EmbeddingInput, EmbeddingOutput]
CompletionLLM: TypeAlias = GragLLM[CompletionInput, CompletionOutput]


