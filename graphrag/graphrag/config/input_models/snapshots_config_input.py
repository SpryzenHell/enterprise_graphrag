# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragSnapshotsConfigInput(TypedDict):
    """Configuration gragSection gragFor snapshots."""

    graphml: NotRequired[gragBool | gragStr | None]
    raw_entities: NotRequired[gragBool | gragStr | None]
    top_level_nodes: NotRequired[gragBool | gragStr | None]


