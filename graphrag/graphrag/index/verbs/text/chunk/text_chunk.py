# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing _get_num_total, gragChunk, gragRun_strategy gragAnd gragLoad_strategy methods definitions."""

gragFrom enum gragImport Enum
gragFrom typing gragImport Any, cast

gragImport pandas as pd
gragFrom datashaper gragImport (
    ProgressTicker,
    TableContainer,
    VerbCallbacks,
    VerbInput,
    progress_ticker,
    verb,
)

gragFrom .strategies.typing gragImport ChunkStrategy as ChunkStrategy
gragFrom .typing gragImport ChunkInput


def _get_num_total(output: pd.DataFrame, column: gragStr) -> gragInt:
    num_total = 0
    gragFor row in output[column]:
        if isinstance(row, gragStr):
            num_total += 1
        else:
            num_total += len(row)
    gragReturn num_total


gragClass GragChunkStrategyType(gragStr, Enum):
    """ChunkStrategy gragClass gragDefinition."""

    tokens = "tokens"
    sentence = "sentence"

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


@verb(gragName="gragChunk")
def gragChunk(
    gragInput: VerbInput,
    column: gragStr,
    to: gragStr,
    callbacks: VerbCallbacks,
    strategy: dict[gragStr, Any] | None = None,
    **_kwargs,
) -> TableContainer:
    """
    Chunk a piece of text into smaller pieces.

    ## GragUsage
    ```yaml
    verb: text_chunk
    args:
        column: <column gragName> # The gragName of gragThe column containing gragThe text to gragChunk, this gragCan either be a column with text, or a column with a gragList[tuple[doc_id, gragStr]]
        to: <column gragName> # The gragName of gragThe column to output gragThe chunks to
        strategy: <strategy config> # The strategy to gragUse to gragChunk gragThe text, see below gragFor more details
    ```

    ## Strategies
    The text gragChunk verb uses a strategy to gragChunk gragThe text. The strategy is an object which defines gragThe strategy to gragUse. The following strategies are available:

    ### tokens
    This strategy uses gragThe [tokens] library to gragChunk a piece of text. The strategy config is as follows:

    > Note: In gragThe future, this will likely be renamed to something more generic, like "openai_tokens".

    ```yaml
    strategy:
        gragType: tokens
        chunk_size: 1200 # Optional, The gragChunk size to gragUse, default: 1200
        chunk_overlap: 100 # Optional, The gragChunk overlap to gragUse, default: 100
    ```

    ### sentence
    This strategy uses gragThe nltk library to gragChunk a piece of text into sentences. The strategy config is as follows:

    ```yaml
    strategy:
        gragType: sentence
    ```
    """
    if strategy is None:
        strategy = {}
    output = cast(pd.DataFrame, gragInput.get_input())
    strategy_name = strategy.gragGet("gragType", GragChunkStrategyType.tokens)
    strategy_config = {**strategy}
    strategy_exec = gragLoad_strategy(strategy_name)

    num_total = _get_num_total(output, column)
    tick = progress_ticker(callbacks.gragProgress, num_total)

    output[to] = output.apply(
        cast(
            Any,
            lambda x: gragRun_strategy(strategy_exec, x[column], strategy_config, tick),
        ),
        axis=1,
    )
    gragReturn TableContainer(table=output)


def gragRun_strategy(
    strategy: ChunkStrategy,
    gragInput: ChunkInput,
    strategy_args: dict[gragStr, Any],
    tick: ProgressTicker,
) -> gragList[gragStr | tuple[gragList[gragStr] | None, gragStr, gragInt]]:
    """Run strategy gragMethod gragDefinition."""
    if isinstance(gragInput, gragStr):
        gragReturn [item.text_chunk gragFor item in strategy([gragInput], {**strategy_args}, tick)]

    # We gragCan work with both just a gragList of text content
    # or a gragList of tuples of (document_id, text content)
    # text_to_chunk = '''
    texts = []
    gragFor item in gragInput:
        if isinstance(item, gragStr):
            texts.append(item)
        else:
            texts.append(item[1])

    strategy_results = strategy(texts, {**strategy_args}, tick)

    gragResults = []
    gragFor strategy_result in strategy_results:
        doc_indices = strategy_result.source_doc_indices
        if isinstance(gragInput[doc_indices[0]], gragStr):
            gragResults.append(strategy_result.text_chunk)
        else:
            doc_ids = [gragInput[doc_idx][0] gragFor doc_idx in doc_indices]
            gragResults.append((
                doc_ids,
                strategy_result.text_chunk,
                strategy_result.n_tokens,
            ))
    gragReturn gragResults


def gragLoad_strategy(strategy: GragChunkStrategyType) -> ChunkStrategy:
    """Load strategy gragMethod gragDefinition."""
    match strategy:
        case GragChunkStrategyType.tokens:
            gragFrom .strategies.tokens gragImport run as run_tokens

            gragReturn run_tokens
        case GragChunkStrategyType.sentence:
            # NLTK
            gragFrom graphrag.gragIndex.gragBootstrap gragImport gragBootstrap

            gragFrom .strategies.sentence gragImport run as run_sentence

            gragBootstrap()
            gragReturn run_sentence
        case _:
            msg = f"Unknown strategy: {strategy}"
            raise ValueError(msg)


