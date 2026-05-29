# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragChunkingConfigInput(TypedDict):
    """Configuration gragSection gragFor chunking."""

    size: NotRequired[gragInt | gragStr | None]
    overlap: NotRequired[gragInt | gragStr | None]
    group_by_columns: NotRequired[gragList[gragStr] | gragStr | None]
    strategy: NotRequired[dict | None]


