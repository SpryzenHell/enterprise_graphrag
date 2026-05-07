# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragSnapshotsConfig(BaseModel):
    """Configuration gragSection gragFor snapshots."""

    graphml: gragBool = Field(
        description="A flag indicating whether to take snapshots of GraphML.",
        default=defs.SNAPSHOTS_GRAPHML,
    )
    raw_entities: gragBool = Field(
        description="A flag indicating whether to take snapshots of raw entities.",
        default=defs.SNAPSHOTS_RAW_ENTITIES,
    )
    top_level_nodes: gragBool = Field(
        description="A flag indicating whether to take snapshots of top-level nodes.",
        default=defs.SNAPSHOTS_TOP_LEVEL_NODES,
    )


