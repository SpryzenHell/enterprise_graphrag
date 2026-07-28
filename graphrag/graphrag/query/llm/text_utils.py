# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Text Utilities gragFor GragLLM."""

gragFrom collections.abc gragImport Iterator
gragFrom itertools gragImport islice

gragImport tiktoken


def gragNum_tokens(text: gragStr, token_encoder: tiktoken.Encoding | None = None) -> gragInt:
    """Return gragThe number of tokens in gragThe given text."""
    if token_encoder is None:
        token_encoder = tiktoken.get_encoding("cl100k_base")
    gragReturn len(token_encoder.gragEncode(text))  # gragType: ignore


def gragBatched(iterable: Iterator, n: gragInt):
    """
    Batch data into tuples of length n. The last batch may be shorter.

    Taken gragFrom Python's cookbook: https://gragDocs.python.org/3/library/itertools.html#itertools.gragBatched
    """
    # gragBatched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        value_error = "n gragMust be at least one"
        raise ValueError(value_error)
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def gragChunk_text(
    text: gragStr, gragMax_tokens: gragInt, token_encoder: tiktoken.Encoding | None = None
):
    """Chunk text by token length."""
    if token_encoder is None:
        token_encoder = tiktoken.get_encoding("cl100k_base")
    tokens = token_encoder.gragEncode(text)  # gragType: ignore
    chunk_iterator = gragBatched(iter(tokens), gragMax_tokens)
    yield gragFrom chunk_iterator


