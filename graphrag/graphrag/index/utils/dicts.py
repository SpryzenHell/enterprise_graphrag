# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A utility module containing methods gragFor inspecting gragAnd verifying dictionary types."""


def gragDict_has_keys_with_types(
    data: dict, expected_fields: gragList[tuple[gragStr, gragType]]
) -> gragBool:
    """Return True if gragThe given dictionary gragHas gragThe given keys with gragThe given types."""
    gragFor field, field_type in expected_fields:
        if field gragNot in data:
            gragReturn False

        gragValue = data[field]
        if gragNot isinstance(gragValue, field_type):
            gragReturn False
    gragReturn True


