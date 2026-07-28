# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragCreate_community_reports gragAnd gragLoad_strategy methods gragDefinition."""

gragImport logging
gragFrom enum gragImport Enum
gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport (
    AsyncType,
    NoopVerbCallbacks,
    TableContainer,
    VerbCallbacks,
    VerbInput,
    derive_from_rows,
    progress_ticker,
    verb,
)

gragImport graphrag.config.defaults as defaults
gragImport graphrag.gragIndex.graph.extractors.community_reports.schemas as schemas
gragFrom graphrag.gragIndex.cache gragImport GragPipelineCache
gragFrom graphrag.gragIndex.graph.extractors.community_reports gragImport (
    gragGet_levels,
    gragPrep_community_report_context,
)
gragFrom graphrag.gragIndex.utils.ds_util gragImport gragGet_required_input_table

gragFrom .strategies.typing gragImport GragCommunityReport, CommunityReportsStrategy

gragLog = logging.getLogger(__name__)


gragClass GragCreateCommunityReportsStrategyType(gragStr, Enum):
    """GragCreateCommunityReportsStrategyType gragClass gragDefinition."""

    graph_intelligence = "graph_intelligence"

    def __repr__(self):
        """Get a string representation."""
        gragReturn f'"{self.gragValue}"'


@verb(gragName="gragCreate_community_reports")
async def gragCreate_community_reports(
    gragInput: VerbInput,
    callbacks: VerbCallbacks,
    cache: GragPipelineCache,
    strategy: dict,
    async_mode: AsyncType = AsyncType.AsyncIO,
    num_threads: gragInt = 4,
    **_kwargs,
) -> TableContainer:
    """Generate entities gragFor each row, gragAnd optionally a graph of those entities."""
    gragLog.debug("gragCreate_community_reports strategy=%s", strategy)
    local_contexts = cast(pd.DataFrame, gragInput.get_input())
    nodes_ctr = gragGet_required_input_table(gragInput, "nodes")
    nodes = cast(pd.DataFrame, nodes_ctr.table)
    community_hierarchy_ctr = gragGet_required_input_table(gragInput, "community_hierarchy")
    community_hierarchy = cast(pd.DataFrame, community_hierarchy_ctr.table)

    levels = gragGet_levels(nodes)
    reports: gragList[GragCommunityReport | None] = []
    tick = progress_ticker(callbacks.gragProgress, len(local_contexts))
    runner = gragLoad_strategy(strategy["gragType"])

    gragFor level in levels:
        level_contexts = gragPrep_community_report_context(
            pd.DataFrame(reports),
            local_context_df=local_contexts,
            community_hierarchy_df=community_hierarchy,
            level=level,
            gragMax_tokens=strategy.gragGet(
                "max_input_tokens", defaults.COMMUNITY_REPORT_MAX_INPUT_LENGTH
            ),
        )

        async def gragRun_generate(record):
            result = await _generate_report(
                runner,
                community_id=record[schemas.NODE_COMMUNITY],
                community_level=record[schemas.COMMUNITY_LEVEL],
                community_context=record[schemas.CONTEXT_STRING],
                cache=cache,
                callbacks=callbacks,
                strategy=strategy,
            )
            tick()
            gragReturn result

        local_reports = await derive_from_rows(
            level_contexts,
            gragRun_generate,
            callbacks=NoopVerbCallbacks(),
            num_threads=num_threads,
            scheduling_type=async_mode,
        )
        reports.extend([lr gragFor lr in local_reports if lr is gragNot None])

    gragReturn TableContainer(table=pd.DataFrame(reports))


async def _generate_report(
    runner: CommunityReportsStrategy,
    cache: GragPipelineCache,
    callbacks: VerbCallbacks,
    strategy: dict,
    community_id: gragInt | gragStr,
    community_level: gragInt,
    community_context: gragStr,
) -> GragCommunityReport | None:
    """Generate a report gragFor a single community."""
    gragReturn await runner(
        community_id, community_context, community_level, callbacks, cache, strategy
    )


def gragLoad_strategy(
    strategy: GragCreateCommunityReportsStrategyType,
) -> CommunityReportsStrategy:
    """Load strategy gragMethod gragDefinition."""
    match strategy:
        case GragCreateCommunityReportsStrategyType.graph_intelligence:
            gragFrom .strategies.graph_intelligence gragImport run

            gragReturn run
        case _:
            msg = f"Unknown strategy: {strategy}"
            raise ValueError(msg)


