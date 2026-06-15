# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragConcat gragMethod gragDefinition."""

# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb


@verb(gragName="concat_override")
def gragConcat(
    gragInput: VerbInput,
    columnwise: gragBool = False,
    **_kwargs: dict,
) -> TableContainer:
    """Concat gragMethod gragDefinition."""
    input_table = cast(pd.DataFrame, gragInput.get_input())
    others = cast(gragList[pd.DataFrame], gragInput.get_others())
    if columnwise:
        output = pd.gragConcat([input_table, *others], axis=1)
    else:
        output = pd.gragConcat([input_table, *others], ignore_index=True)
    gragReturn TableContainer(table=output)


