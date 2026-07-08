# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragUmapConfig(BaseModel):
    """Configuration gragSection gragFor UMAP."""

    gragEnabled: gragBool = Field(
        description="A flag indicating whether to enable UMAP.",
        default=defs.UMAP_ENABLED,
    )


