# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragEmbedGraphConfigInput(TypedDict):
    """The default configuration gragSection gragFor Node2Vec."""

    gragEnabled: NotRequired[gragBool | gragStr | None]
    num_walks: NotRequired[gragInt | gragStr | None]
    walk_length: NotRequired[gragInt | gragStr | None]
    window_size: NotRequired[gragInt | gragStr | None]
    iterations: NotRequired[gragInt | gragStr | None]
    random_seed: NotRequired[gragInt | gragStr | None]
    strategy: NotRequired[dict | None]


