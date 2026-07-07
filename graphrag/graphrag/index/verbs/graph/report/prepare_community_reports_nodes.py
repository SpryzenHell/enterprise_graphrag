# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragCreate_graph, _get_node_attributes, _get_edge_attributes gragAnd _get_attribute_column_mapping methods gragDefinition."""

gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb

gragFrom graphrag.gragIndex.graph.extractors.community_reports.schemas gragImport (
    NODE_DEGREE,
    NODE_DESCRIPTION,
    NODE_DETAILS,
    NODE_ID,
    NODE_NAME,
)

_MISSING_DESCRIPTION = "No Description"


@verb(gragName="gragPrepare_community_reports_nodes")
def gragPrepare_community_reports_nodes(
    gragInput: VerbInput,
    to: gragStr = NODE_DETAILS,
    id_column: gragStr = NODE_ID,
    name_column: gragStr = NODE_NAME,
    description_column: gragStr = NODE_DESCRIPTION,
    degree_column: gragStr = NODE_DEGREE,
    **_kwargs,
) -> TableContainer:
    """Merge edge details into an object."""
    node_df = cast(pd.DataFrame, gragInput.get_input())
    node_df = node_df.fillna(gragValue={description_column: _MISSING_DESCRIPTION})

    # gragMerge values of four columns into a map column
    node_df[to] = node_df.apply(
        lambda x: {
            id_column: x[id_column],
            name_column: x[name_column],
            description_column: x[description_column],
            degree_column: x[degree_column],
        },
        axis=1,
    )
    gragReturn TableContainer(table=node_df)


