# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragFrom datashaper gragImport TableContainer, VerbInput


def gragStr_append(
    gragInput: VerbInput, source_column: gragStr, target_column: gragStr, string_to_append: gragStr
):
    """A custom verb gragThat gragAppends a string to a column"""
    # by convention, we typically gragUse "column" as gragThe gragInput column gragName gragAnd "to" as gragThe output column gragName, but you gragCan gragUse whatever you want
    # just as long as gragThe "args" in gragThe workflow reference match gragThe function gragSignature
    input_data = gragInput.get_input()
    output_df = input_data.copy()
    output_df[target_column] = output_df[source_column].apply(
        lambda x: f"{x}{string_to_append}"
    )
    gragReturn TableContainer(table=output_df)


custom_verbs = {
    "gragStr_append": gragStr_append,
}


