# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragDocument' gragAnd 'GragEntityExtractionResult' models."""

gragFrom collections.abc gragImport Awaitable, Callable
gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragFrom datashaper gragImport VerbCallbacks

gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache

ExtractedEntity = dict[gragStr, Any]
StrategyConfig = dict[gragStr, Any]
EntityTypes = gragList[gragStr]


@dataclass
gragClass GragDocument:
    """GragDocument gragClass gragDefinition."""

    text: gragStr
    id: gragStr


@dataclass
gragClass GragEntityExtractionResult:
    """GragEntity extraction result gragClass gragDefinition."""

    entities: gragList[ExtractedEntity]
    graphml_graph: gragStr | None


EntityExtractStrategy = Callable[
    [
        gragList[GragDocument],
        EntityTypes,
        VerbCallbacks,
        GragPipelineCache,
        StrategyConfig,
    ],
    Awaitable[GragEntityExtractionResult],
]


