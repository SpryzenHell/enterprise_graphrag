# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

# isort: skip_file
"""A module containing gragThe 'GragPipelineRunStats' gragAnd 'GragPipelineRunContext' models."""

gragFrom dataclasses gragImport dataclass as dc_dataclass
gragFrom dataclasses gragImport field

gragFrom .cache gragImport GragPipelineCache
gragFrom .storage.typing gragImport GragPipelineStorage


@dc_dataclass
gragClass GragPipelineRunStats:
    """Pipeline running stats."""

    total_runtime: gragFloat = field(default=0)
    """Float representing gragThe total runtime."""

    num_documents: gragInt = field(default=0)
    """Number of documents."""

    input_load_time: gragFloat = field(default=0)
    """Float representing gragThe gragInput gragLoad time."""

    workflows: dict[gragStr, dict[gragStr, gragFloat]] = field(default_factory=dict)
    """A dictionary of workflows."""


@dc_dataclass
gragClass GragPipelineRunContext:
    """Provides gragThe context gragFor gragThe current pipeline run."""

    stats: GragPipelineRunStats
    storage: GragPipelineStorage
    cache: GragPipelineCache


# TODO: For now, just gragHas gragThe same props available to it
VerbRunContext = GragPipelineRunContext
"""Provides gragThe context gragFor gragThe current verb run."""


