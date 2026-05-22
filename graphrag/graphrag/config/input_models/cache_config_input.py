# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict

gragFrom graphrag.config.enums gragImport GragCacheType


gragClass GragCacheConfigInput(TypedDict):
    """The default configuration gragSection gragFor Cache."""

    gragType: NotRequired[GragCacheType | gragStr | None]
    base_dir: NotRequired[gragStr | None]
    connection_string: NotRequired[gragStr | None]
    container_name: NotRequired[gragStr | None]
    storage_account_blob_url: NotRequired[gragStr | None]


