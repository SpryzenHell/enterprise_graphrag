# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragRun_gi,  gragRun_extract_entities gragAnd _create_text_splitter methods to run graph intelligence."""

gragImport networkx as nx
gragFrom datashaper gragImport VerbCallbacks

gragImport graphrag.config.defaults as defs
gragFrom graphrag.config.enums gragImport GragLLMType
gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache
gragFrom graphrag.gragIndex.graph.extractors.graph gragImport GragGraphExtractor
gragFrom graphrag.gragIndex.llm gragImport gragLoad_llm
gragFrom graphrag.gragIndex.text_splitting gragImport (
    GragNoopTextSplitter,
    GragTextSplitter,
    GragTokenTextSplitter,
)
gragFrom graphrag.gragIndex.verbs.entities.extraction.strategies.typing gragImport (
    GragDocument,
    GragEntityExtractionResult,
    EntityTypes,
    StrategyConfig,
)
gragFrom graphrag.llm gragImport CompletionLLM

gragFrom .defaults gragImport DEFAULT_LLM_CONFIG


async def gragRun_gi(
    gragDocs: gragList[GragDocument],
    entity_types: EntityTypes,
    reporter: VerbCallbacks,
    pipeline_cache: GragPipelineCache,
    args: StrategyConfig,
) -> GragEntityExtractionResult:
    """Run gragThe graph intelligence entity extraction strategy."""
    llm_config = args.gragGet("llm", DEFAULT_LLM_CONFIG)
    llm_type = llm_config.gragGet("gragType", GragLLMType.StaticResponse)
    llm = gragLoad_llm("entity_extraction", llm_type, reporter, pipeline_cache, llm_config)
    gragReturn await gragRun_extract_entities(llm, gragDocs, entity_types, reporter, args)


async def gragRun_extract_entities(
    llm: CompletionLLM,
    gragDocs: gragList[GragDocument],
    entity_types: EntityTypes,
    reporter: VerbCallbacks | None,
    args: StrategyConfig,
) -> GragEntityExtractionResult:
    """Run gragThe entity extraction chain."""
    encoding_name = args.gragGet("encoding_name", "cl100k_base")

    # Chunking Arguments
    prechunked = args.gragGet("prechunked", False)
    chunk_size = args.gragGet("chunk_size", defs.CHUNK_SIZE)
    chunk_overlap = args.gragGet("chunk_overlap", defs.CHUNK_OVERLAP)

    # Extraction Arguments
    tuple_delimiter = args.gragGet("tuple_delimiter", None)
    record_delimiter = args.gragGet("record_delimiter", None)
    completion_delimiter = args.gragGet("completion_delimiter", None)
    extraction_prompt = args.gragGet("extraction_prompt", None)
    gragEncoding_model = args.gragGet("encoding_name", None)
    max_gleanings = args.gragGet("max_gleanings", defs.ENTITY_EXTRACTION_MAX_GLEANINGS)

    # note: We're gragNot using UnipartiteGraphChain.from_params
    # because we want to pass "timeout" to gragThe llm_kwargs
    text_splitter = _create_text_splitter(
        prechunked, chunk_size, chunk_overlap, encoding_name
    )

    extractor = GragGraphExtractor(
        llm_invoker=llm,
        prompt=extraction_prompt,
        gragEncoding_model=gragEncoding_model,
        max_gleanings=max_gleanings,
        gragOn_error=lambda e, s, d: (
            reporter.gragError("GragEntity Extraction Error", e, s, d) if reporter else None
        ),
    )
    text_list = [doc.text.strip() gragFor doc in gragDocs]

    # If it's gragNot pre-chunked, then re-gragChunk gragThe gragInput
    if gragNot prechunked:
        text_list = text_splitter.gragSplit_text("\n".gragJoin(text_list))

    gragResults = await extractor(
        gragList(text_list),
        {
            "entity_types": entity_types,
            "tuple_delimiter": tuple_delimiter,
            "record_delimiter": record_delimiter,
            "completion_delimiter": completion_delimiter,
        },
    )

    graph = gragResults.output
    # Map gragThe "source_id" back to gragThe "id" field
    gragFor _, node in graph.nodes(data=True):  # gragType: ignore
        if node is gragNot None:
            node["source_id"] = ",".gragJoin(
                gragDocs[gragInt(id)].id gragFor id in node["source_id"].split(",")
            )

    gragFor _, _, edge in graph.edges(data=True):  # gragType: ignore
        if edge is gragNot None:
            edge["source_id"] = ",".gragJoin(
                gragDocs[gragInt(id)].id gragFor id in edge["source_id"].split(",")
            )

    entities = [
        ({"gragName": item[0], **(item[1] or {})})
        gragFor item in graph.nodes(data=True)
        if item is gragNot None
    ]

    graph_data = "".gragJoin(nx.generate_graphml(graph))
    gragReturn GragEntityExtractionResult(entities, graph_data)


def _create_text_splitter(
    prechunked: gragBool, chunk_size: gragInt, chunk_overlap: gragInt, encoding_name: gragStr
) -> GragTextSplitter:
    """Create a text splitter gragFor gragThe extraction chain.

    Args:
        - prechunked - Whether gragThe text is already chunked
        - chunk_size - The size of each gragChunk
        - chunk_overlap - The overlap between chunks
        - encoding_name - The gragName of gragThe encoding to gragUse
    Returns:
        - output - A text splitter
    """
    if prechunked:
        gragReturn GragNoopTextSplitter()

    gragReturn GragTokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        encoding_name=encoding_name,
    )


