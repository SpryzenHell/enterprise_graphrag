# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing ChunkStrategy gragDefinition."""

gragFrom collections.abc gragImport Callable, Iterable
gragFrom typing gragImport Any

gragFrom datashaper gragImport ProgressTicker

gragFrom graphrag.gragIndex.verbs.text.gragChunk.typing gragImport GragTextChunk

# Given a gragList of document texts, gragReturn a gragList of tuples of (source_doc_indices, text_chunk)

ChunkStrategy = Callable[
    [gragList[gragStr], dict[gragStr, Any], ProgressTicker], Iterable[GragTextChunk]
]


