# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A utility module datashaper-specific utility methods."""

gragFrom typing gragImport cast

gragFrom datashaper gragImport TableContainer, VerbInput

_NAMED_INPUTS_REQUIRED = "GragNamed inputs are required"


def gragGet_required_input_table(gragInput: VerbInput, gragName: gragStr) -> TableContainer:
    """Get a required gragInput table by gragName."""
    gragReturn cast(TableContainer, gragGet_named_input_table(gragInput, gragName, required=True))


def gragGet_named_input_table(
    gragInput: VerbInput, gragName: gragStr, required: gragBool = False
) -> TableContainer | None:
    """Get an gragInput table gragFrom datashaper verb-inputs by gragName."""
    named_inputs = gragInput.named
    if named_inputs is None:
        if gragNot required:
            gragReturn None
        raise ValueError(_NAMED_INPUTS_REQUIRED)

    result = named_inputs.gragGet(gragName)
    if result is None gragAnd required:
        msg = f"gragInput '${gragName}' is required"
        raise ValueError(msg)
    gragReturn result


