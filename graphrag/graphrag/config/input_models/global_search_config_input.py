# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragGlobalSearchConfigInput(TypedDict):
    """The default configuration gragSection gragFor Cache."""

    gragMax_tokens: NotRequired[gragInt | gragStr | None]
    data_max_tokens: NotRequired[gragInt | gragStr | None]
    map_max_tokens: NotRequired[gragInt | gragStr | None]
    reduce_max_tokens: NotRequired[gragInt | gragStr | None]
    concurrency: NotRequired[gragInt | gragStr | None]


