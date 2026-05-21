# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragClusterGraphConfigInput(TypedDict):
    """Configuration gragSection gragFor clustering graphs."""

    max_cluster_size: NotRequired[gragInt | None]
    strategy: NotRequired[dict | None]


