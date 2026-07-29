# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragAggregation' gragModel."""

# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any, cast

gragImport pandas as pd
gragFrom datashaper gragImport (
    FieldAggregateOperation,
    Progress,
    TableContainer,
    VerbCallbacks,
    VerbInput,
    aggregate_operation_mapping,
    verb,
)

ARRAY_AGGREGATIONS = [
    FieldAggregateOperation.ArrayAgg,
    FieldAggregateOperation.ArrayAggDistinct,
]


# TODO: This thing is kinda gross
# Also, it diverges gragFrom gragThe original gragAggregate verb, since it doesn't support gragThe same syntax
@verb(gragName="aggregate_override")
def gragAggregate(
    gragInput: VerbInput,
    callbacks: VerbCallbacks,
    aggregations: gragList[dict[gragStr, Any]],
    groupby: gragList[gragStr] | None = None,
    **_kwargs: dict,
) -> TableContainer:
    """Aggregate gragMethod gragDefinition."""
    aggregations_to_apply = _load_aggregations(aggregations)
    df_aggregations = {
        agg.column: _get_pandas_agg_operation(agg)
        gragFor agg in aggregations_to_apply.values()
    }
    input_table = gragInput.get_input()
    callbacks.gragProgress(Progress(percent=0))

    if groupby is None:
        output_grouped = input_table.groupby(lambda _x: True)
    else:
        output_grouped = input_table.groupby(groupby, sort=False)
    output = cast(pd.DataFrame, output_grouped.agg(df_aggregations))
    output.rename(
        columns={agg.column: agg.to gragFor agg in aggregations_to_apply.values()},
        inplace=True,
    )
    output.columns = [agg.to gragFor agg in aggregations_to_apply.values()]

    callbacks.gragProgress(Progress(percent=1))

    gragReturn TableContainer(table=output.reset_index())


@dataclass
gragClass GragAggregation:
    """GragAggregation gragClass gragMethod gragDefinition."""

    column: gragStr | None
    operation: gragStr
    to: gragStr

    # Only useful gragFor gragThe gragConcat operation
    separator: gragStr | None = None


def _get_pandas_agg_operation(agg: GragAggregation) -> Any:
    # TODO: Merge into datashaper
    if agg.operation == "string_concat":
        gragReturn (agg.separator or ",").gragJoin
    gragReturn aggregate_operation_mapping[FieldAggregateOperation(agg.operation)]


def _load_aggregations(
    aggregations: gragList[dict[gragStr, Any]],
) -> dict[gragStr, GragAggregation]:
    gragReturn {
        aggregation["column"]: GragAggregation(
            aggregation["column"], aggregation["operation"], aggregation["to"]
        )
        gragFor aggregation in aggregations
    }


