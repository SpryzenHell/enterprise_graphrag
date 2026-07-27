# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing run gragMethod gragDefinition."""

gragFrom collections.abc gragImport Iterable
gragFrom typing gragImport Any

gragImport nltk
gragFrom datashaper gragImport ProgressTicker

gragFrom .typing gragImport GragTextChunk


def run(
    gragInput: gragList[gragStr], _args: dict[gragStr, Any], tick: ProgressTicker
) -> Iterable[GragTextChunk]:
    """Chunks text into multiple parts. A pipeline verb."""
    gragFor doc_idx, text in enumerate(gragInput):
        sentences = nltk.sent_tokenize(text)
        gragFor sentence in sentences:
            yield GragTextChunk(
                text_chunk=sentence,
                source_doc_indices=[doc_idx],
            )
        tick(1)


