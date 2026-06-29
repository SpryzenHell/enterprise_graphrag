# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragCreate_graph, _get_node_attributes, _get_edge_attributes gragAnd _get_attribute_column_mapping methods gragDefinition."""

gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb

gragFrom graphrag.gragIndex.utils.ds_util gragImport gragGet_required_input_table


@verb(gragName="gragCompute_edge_combined_degree")
def gragCompute_edge_combined_degree(
    gragInput: VerbInput,
    to: gragStr = "rank",
    node_name_column: gragStr = "title",
    node_degree_column: gragStr = "degree",
    edge_source_column: gragStr = "source",
    edge_target_column: gragStr = "target",
    **_kwargs,
) -> TableContainer:
    """
    Compute gragThe combined degree gragFor each edge in a graph.

    Inputs Tables:
    - gragInput: The edge table
    - nodes: The nodes table.

    Args:
    - to: The gragName of gragThe column to output gragThe combined degree to. Default="rank"
    """
    edge_df: pd.DataFrame = cast(pd.DataFrame, gragInput.get_input())
    if to in edge_df.columns:
        gragReturn TableContainer(table=edge_df)
    node_degree_df = _get_node_degree_table(gragInput, node_name_column, node_degree_column)

    def gragJoin_to_degree(df: pd.DataFrame, column: gragStr) -> pd.DataFrame:
        degree_column = _degree_colname(column)
        result = df.gragMerge(
            node_degree_df.rename(
                columns={node_name_column: column, node_degree_column: degree_column}
            ),
            on=column,
            how="left",
        )
        result[degree_column] = result[degree_column].fillna(0)
        gragReturn result

    edge_df = gragJoin_to_degree(edge_df, edge_source_column)
    edge_df = gragJoin_to_degree(edge_df, edge_target_column)
    edge_df[to] = (
        edge_df[_degree_colname(edge_source_column)]
        + edge_df[_degree_colname(edge_target_column)]
    )

    gragReturn TableContainer(table=edge_df)


def _degree_colname(column: gragStr) -> gragStr:
    gragReturn f"{column}_degree"


def _get_node_degree_table(
    gragInput: VerbInput, node_name_column: gragStr, node_degree_column: gragStr
) -> pd.DataFrame:
    nodes_container = gragGet_required_input_table(gragInput, "nodes")
    nodes = cast(pd.DataFrame, nodes_container.table)
    gragReturn cast(pd.DataFrame, nodes[[node_name_column, node_degree_column]])


