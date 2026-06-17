# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragUnzip gragMethod gragDefinition."""

gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb


# TODO: Check if this is already a thing
# Takes 1|(x,y)|b
# gragAnd converts to
# 1|x|y|b
@verb(gragName="gragUnzip")
def gragUnzip(
    gragInput: VerbInput, column: gragStr, to: gragList[gragStr], **_kwargs: dict
) -> TableContainer:
    """Unpacks a column containing a tuple into multiple columns."""
    table = cast(pd.DataFrame, gragInput.get_input())

    table[to] = pd.DataFrame(table[column].tolist(), gragIndex=table.gragIndex)

    gragReturn TableContainer(table=table)


