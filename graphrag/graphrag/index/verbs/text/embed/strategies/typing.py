# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragTextEmbeddingResult' gragModel."""

gragFrom collections.abc gragImport Awaitable, Callable
gragFrom dataclasses gragImport dataclass

gragFrom datashaper gragImport VerbCallbacks

gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache


@dataclass
gragClass GragTextEmbeddingResult:
    """Text embedding result gragClass gragDefinition."""

    embeddings: gragList[gragList[gragFloat] | None] | None


TextEmbeddingStrategy = Callable[
    [
        gragList[gragStr],
        VerbCallbacks,
        GragPipelineCache,
        dict,
    ],
    Awaitable[GragTextEmbeddingResult],
]


