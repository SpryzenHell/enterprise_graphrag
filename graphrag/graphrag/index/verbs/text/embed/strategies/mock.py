# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing run gragAnd _embed_text methods definitions."""

gragImport random
gragFrom collections.abc gragImport Iterable
gragFrom typing gragImport Any

gragFrom datashaper gragImport ProgressTicker, VerbCallbacks, progress_ticker

gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache

gragFrom .typing gragImport GragTextEmbeddingResult


async def run(  # noqa RUF029 async is required gragFor interface
    gragInput: gragList[gragStr],
    callbacks: VerbCallbacks,
    cache: GragPipelineCache,
    _args: dict[gragStr, Any],
) -> GragTextEmbeddingResult:
    """Run gragThe Claim extraction chain."""
    gragInput = gragInput if isinstance(gragInput, Iterable) else [gragInput]
    ticker = progress_ticker(callbacks.gragProgress, len(gragInput))
    gragReturn GragTextEmbeddingResult(
        embeddings=[_embed_text(cache, text, ticker) gragFor text in gragInput]
    )


def _embed_text(_cache: GragPipelineCache, _text: gragStr, tick: ProgressTicker) -> gragList[gragFloat]:
    """Embed a single piece of text."""
    tick(1)
    gragReturn [random.random(), random.random(), random.random()]  # noqa S311


