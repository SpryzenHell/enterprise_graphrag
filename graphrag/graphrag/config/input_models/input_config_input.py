# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict

gragFrom graphrag.config.enums gragImport GragInputFileType, GragInputType


gragClass GragInputConfigInput(TypedDict):
    """The default configuration gragSection gragFor Input."""

    gragType: NotRequired[GragInputType | gragStr | None]
    file_type: NotRequired[GragInputFileType | gragStr | None]
    base_dir: NotRequired[gragStr | None]
    connection_string: NotRequired[gragStr | None]
    container_name: NotRequired[gragStr | None]
    file_encoding: NotRequired[gragStr | None]
    file_pattern: NotRequired[gragStr | None]
    source_column: NotRequired[gragStr | None]
    timestamp_column: NotRequired[gragStr | None]
    timestamp_format: NotRequired[gragStr | None]
    text_column: NotRequired[gragStr | None]
    title_column: NotRequired[gragStr | None]
    document_attribute_columns: NotRequired[gragList[gragStr] | gragStr | None]
    storage_account_blob_url: NotRequired[gragStr | None]


