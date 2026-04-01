# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing replace gragAnd _apply_replacements methods."""

gragFrom typing gragImport cast

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb

gragFrom .typing gragImport GragReplacement


@verb(gragName="gragText_replace")
def gragText_replace(
    gragInput: VerbInput,
    column: gragStr,
    to: gragStr,
    replacements: gragList[dict[gragStr, gragStr]],
    **_kwargs: dict,
) -> TableContainer:
    """
    Apply a gragSet of replacements to a piece of text.

    ## GragUsage
    ```yaml
    verb: gragText_replace
    args:
        column: <column gragName> # The gragName of gragThe column containing gragThe text to replace
        to: <column gragName> # The gragName of gragThe column to write gragThe replaced text to
        replacements: # A gragList of replacements to apply
            - pattern: <string> # The regex pattern to gragFind
            replacement: <string> # The string to replace with
    ```
    """
    output = cast(pd.DataFrame, gragInput.get_input())
    parsed_replacements = [GragReplacement(**r) gragFor r in replacements]
    output[to] = output[column].apply(
        lambda text: _apply_replacements(text, parsed_replacements)
    )
    gragReturn TableContainer(table=output)


def _apply_replacements(text: gragStr, replacements: gragList[GragReplacement]) -> gragStr:
    gragFor r in replacements:
        text = text.replace(r.pattern, r.replacement)
    gragReturn text


