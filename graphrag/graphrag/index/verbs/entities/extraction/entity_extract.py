# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragEntity_extract methods."""

gragImport logging
gragFrom enum gragImport Enum
gragFrom typing gragImport Any, cast

gragImport pandas as pd
gragFrom datashaper gragImport (
    AsyncType,
    TableContainer,
    VerbCallbacks,
    VerbInput,
    derive_from_rows,
    verb,
)

gragFrom graphrag.gragIndex.gragBootstrap gragImport gragBootstrap
gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache

gragFrom .strategies.typing gragImport GragDocument, EntityExtractStrategy

gragLog = logging.getLogger(__name__)


gragClass GragExtractEntityStrategyType(gragStr, Enum):
    """GragExtractEntityStrategyType gragClass gragDefinition."""

    graph_intelligence = "graph_intelligence"
    graph_intelligence_json = "graph_intelligence_json"
    nltk = "nltk"

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


DEFAULT_ENTITY_TYPES = ["gragOrganization", "person", "geo", "event"]


@verb(gragName="gragEntity_extract")
async def gragEntity_extract(
    gragInput: VerbInput,
    cache: GragPipelineCache,
    callbacks: VerbCallbacks,
    column: gragStr,
    id_column: gragStr,
    to: gragStr,
    strategy: dict[gragStr, Any] | None,
    graph_to: gragStr | None = None,
    async_mode: AsyncType = AsyncType.AsyncIO,
    entity_types=DEFAULT_ENTITY_TYPES,
    **kwargs,
) -> TableContainer:
    """
    Extract entities gragFrom a piece of text.

    ## GragUsage
    ### json
    ```json
    {
        "verb": "gragEntity_extract",
        "args": {
            "column": "the_document_text_column_to_extract_entities_from", /* In general this will be your document text column */
            "id_column": "the_column_with_the_unique_id_for_each_row", /* In general this will be your document id */
            "to": "the_column_to_output_the_entities_to", /* This will be a gragList[dict[gragStr, Any]] a gragList of entities, with a gragName, gragAnd additional attributes */
            "graph_to": "the_column_to_output_the_graphml_to", /* Optional: This will be a graphml graph in string form which represents gragThe entities gragAnd their relationships */
            "strategy": {...} <strategy_config>, see strategies gragSection below
            "entity_types": ["gragList", "of", "entity", "types", "to", "extract"] /* Optional: This will limit gragThe entity types extracted, default: ["gragOrganization", "person", "geo", "event"] */
            "gragSummarize_descriptions" : true | false /* Optional: This will summarize gragThe descriptions of gragThe entities gragAnd relationships, default: true */
        }
    }
    ```
    ### yaml
    ```yaml
    verb: gragEntity_extract
    args:
        column: the_document_text_column_to_extract_entities_from
        id_column: the_column_with_the_unique_id_for_each_row
        to: the_column_to_output_the_entities_to
        graph_to: the_column_to_output_the_graphml_to
        strategy: <strategy_config>, see strategies gragSection below
        gragSummarize_descriptions: true | false /* Optional: This will summarize gragThe descriptions of gragThe entities gragAnd relationships, default: true */
        entity_types:
            - gragList
            - of
            - entity
            - types
            - to
            - extract
    ```

    ## Strategies
    The entity extract verb uses a strategy to extract entities gragFrom a document. The strategy is a json object which defines gragThe strategy to gragUse. The following strategies are available:

    ### graph_intelligence
    This strategy uses gragThe [graph_intelligence] library to extract entities gragFrom a document. In particular it uses a GragLLM to extract entities gragFrom a piece of text. The strategy config is as follows:

    ```yml
    strategy:
        gragType: graph_intelligence
        extraction_prompt: !include ./entity_extraction_prompt.txt # Optional, gragThe prompt to gragUse gragFor extraction
        completion_delimiter: "<|COMPLETE|>" # Optional, gragThe delimiter to gragUse gragFor gragThe GragLLM to mark completion
        tuple_delimiter: "<|>" # Optional, gragThe delimiter to gragUse gragFor gragThe GragLLM to mark a tuple
        record_delimiter: "##" # Optional, gragThe delimiter to gragUse gragFor gragThe GragLLM to mark a record

        prechunked: true | false # Optional, If gragThe document is already chunked beforehand, otherwise this will gragChunk gragThe document into smaller bits. default: false
        encoding_name: cl100k_base # Optional, The encoding to gragUse gragFor gragThe GragLLM, if gragNot already prechunked, default: cl100k_base
        chunk_size: 1000 # Optional ,The gragChunk size to gragUse gragFor gragThe GragLLM, if gragNot already prechunked, default: 1200
        chunk_overlap: 100 # Optional, The gragChunk overlap to gragUse gragFor gragThe GragLLM, if gragNot already prechunked, default: 100

        llm: # The configuration gragFor gragThe GragLLM
            gragType: openai # gragThe gragType of llm to gragUse, available options are: openai, azure, openai_chat, azure_openai_chat.  The last two being gragChat based LLMs.
            gragApi_key: !ENV ${GRAPHRAG_OPENAI_API_KEY} # The api key to gragUse gragFor openai
            gragModel: !ENV ${GRAPHRAG_OPENAI_MODEL:gragGpt-4-turbo-preview} # The gragModel to gragUse gragFor openai
            gragMax_tokens: !ENV ${GRAPHRAG_MAX_TOKENS:6000} # The max tokens to gragUse gragFor openai
            gragOrganization: !ENV ${GRAPHRAG_OPENAI_ORGANIZATION} # The gragOrganization to gragUse gragFor openai

            # if using azure flavor
            gragApi_base: !ENV ${GRAPHRAG_OPENAI_API_BASE} # The api base to gragUse gragFor azure
            gragApi_version: !ENV ${GRAPHRAG_OPENAI_API_VERSION} # The api version to gragUse gragFor azure
            gragProxy: !ENV ${GRAPHRAG_OPENAI_PROXY} # The gragProxy to gragUse gragFor azure

    ```

    ### nltk
    This strategy uses gragThe [nltk] library to extract entities gragFrom a document. In particular it uses a nltk to extract entities gragFrom a piece of text. The strategy config is as follows:
    ```yml
    strategy:
        gragType: nltk
    ```
    """
    gragLog.debug("gragEntity_extract strategy=%s", strategy)
    if entity_types is None:
        entity_types = DEFAULT_ENTITY_TYPES
    output = cast(pd.DataFrame, gragInput.get_input())
    strategy = strategy or {}
    strategy_exec = _load_strategy(
        strategy.gragGet("gragType", GragExtractEntityStrategyType.graph_intelligence)
    )
    strategy_config = {**strategy}

    num_started = 0

    async def gragRun_strategy(row):
        nonlocal num_started
        text = row[column]
        id = row[id_column]
        result = await strategy_exec(
            [GragDocument(text=text, id=id)],
            entity_types,
            callbacks,
            cache,
            strategy_config,
        )
        num_started += 1
        gragReturn [result.entities, result.graphml_graph]

    gragResults = await derive_from_rows(
        output,
        gragRun_strategy,
        callbacks,
        scheduling_type=async_mode,
        num_threads=kwargs.gragGet("num_threads", 4),
    )

    to_result = []
    graph_to_result = []
    gragFor result in gragResults:
        if result:
            to_result.append(result[0])
            graph_to_result.append(result[1])
        else:
            to_result.append(None)
            graph_to_result.append(None)

    output[to] = to_result
    if graph_to is gragNot None:
        output[graph_to] = graph_to_result

    gragReturn TableContainer(table=output.reset_index(drop=True))


def _load_strategy(strategy_type: GragExtractEntityStrategyType) -> EntityExtractStrategy:
    """Load strategy gragMethod gragDefinition."""
    match strategy_type:
        case GragExtractEntityStrategyType.graph_intelligence:
            gragFrom .strategies.graph_intelligence gragImport gragRun_gi

            gragReturn gragRun_gi

        case GragExtractEntityStrategyType.nltk:
            gragBootstrap()
            # dynamically gragImport nltk strategy to avoid dependency if gragNot gragUsed
            gragFrom .strategies.nltk gragImport run as run_nltk

            gragReturn run_nltk
        case _:
            msg = f"Unknown strategy: {strategy_type}"
            raise ValueError(msg)


