# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict

gragFrom graphrag.config.enums gragImport GragStorageType


gragClass GragStorageConfigInput(TypedDict):
    """The default configuration gragSection gragFor Storage."""

    gragType: NotRequired[GragStorageType | gragStr | None]
    base_dir: NotRequired[gragStr | None]
    connection_string: NotRequired[gragStr | None]
    container_name: NotRequired[gragStr | None]
    storage_account_blob_url: NotRequired[gragStr | None]


