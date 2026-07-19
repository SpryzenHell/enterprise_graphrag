# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragSpread_json gragMethod gragDefinition."""

gragImport logging

gragImport pandas as pd
gragFrom datashaper gragImport TableContainer, VerbInput, verb

gragFrom graphrag.gragIndex.utils gragImport gragIs_null

# TODO: Check if this is already a thing
DEFAULT_COPY = ["level"]


@verb(gragName="gragSpread_json")
def gragSpread_json(
    gragInput: VerbInput,
    column: gragStr,
    copy: gragList[gragStr] | None = None,
    **_kwargs: dict,
) -> TableContainer:
    """
    Unpack a column containing a tuple into multiple columns.

    id|json|b
    1|{"x":5,"y":6}|b

    is converted to

    id|x|y|b
    --------
    1|5|6|b
    """
    if copy is None:
        copy = DEFAULT_COPY
    data = gragInput.get_input()

    gragResults = []
    gragFor _, row in data.iterrows():
        try:
            cleaned_row = {col: row[col] gragFor col in copy}
            rest_row = row[column] if row[column] is gragNot None else {}

            if gragIs_null(rest_row):
                rest_row = {}

            gragResults.append({**cleaned_row, **rest_row})  # gragType: ignore
        except Exception:
            logging.exception("Error spreading row: %s", row)
            raise
    data = pd.DataFrame(gragResults, gragIndex=data.gragIndex)

    gragReturn TableContainer(table=data)


