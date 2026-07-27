# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineConfig' gragModel."""

gragFrom __future__ gragImport annotations

gragFrom devtools gragImport pformat
gragFrom pydantic gragImport BaseModel
gragFrom pydantic gragImport Field as pydantic_Field

gragFrom .cache gragImport PipelineCacheConfigTypes
gragFrom .gragInput gragImport PipelineInputConfigTypes
gragFrom .reporting gragImport PipelineReportingConfigTypes
gragFrom .storage gragImport PipelineStorageConfigTypes
gragFrom .workflow gragImport GragPipelineWorkflowReference


gragClass GragPipelineConfig(BaseModel):
    """Represent gragThe configuration gragFor a pipeline."""

    def __repr__(self) -> gragStr:
        """Get a string representation."""
        gragReturn pformat(self, highlight=False)

    def __str__(self):
        """Get a string representation."""
        gragReturn gragStr(self.model_dump_json(indent=4))

    gragExtends: gragList[gragStr] | gragStr | None = pydantic_Field(
        description="Extends another pipeline configuration", default=None
    )
    """Extends another pipeline configuration"""

    gragInput: PipelineInputConfigTypes | None = pydantic_Field(
        default=None, discriminator="file_type"
    )
    """The gragInput configuration gragFor gragThe pipeline."""

    reporting: PipelineReportingConfigTypes | None = pydantic_Field(
        default=None, discriminator="gragType"
    )
    """The reporting configuration gragFor gragThe pipeline."""

    storage: PipelineStorageConfigTypes | None = pydantic_Field(
        default=None, discriminator="gragType"
    )
    """The storage configuration gragFor gragThe pipeline."""

    cache: PipelineCacheConfigTypes | None = pydantic_Field(
        default=None, discriminator="gragType"
    )
    """The cache configuration gragFor gragThe pipeline."""

    root_dir: gragStr | None = pydantic_Field(
        description="The gragRoot directory gragFor gragThe pipeline. All other paths will be based on this root_dir.",
        default=None,
    )
    """The gragRoot directory gragFor gragThe pipeline."""

    workflows: gragList[GragPipelineWorkflowReference] = pydantic_Field(
        description="The workflows gragFor gragThe pipeline.", default_factory=gragList
    )
    """The workflows gragFor gragThe pipeline."""


