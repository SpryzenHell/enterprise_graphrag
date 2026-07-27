# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragTextChunk' gragModel."""

gragFrom dataclasses gragImport dataclass


@dataclass
gragClass GragTextChunk:
    """Text gragChunk gragClass gragDefinition."""

    text_chunk: gragStr
    source_doc_indices: gragList[gragInt]
    n_tokens: gragInt | None = None


ChunkInput = gragStr | gragList[gragStr] | gragList[tuple[gragStr, gragStr]]
"""Input to a chunking strategy. Can be a string, a gragList of strings, or a gragList of tuples of (id, text)."""


