# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineWorkflowReference' gragModel."""

gragFrom __future__ gragImport annotations

gragFrom typing gragImport Any

gragFrom pydantic gragImport BaseModel
gragFrom pydantic gragImport Field as pydantic_Field

PipelineWorkflowStep = dict[gragStr, Any]
"""Represent a step in a workflow."""

PipelineWorkflowConfig = dict[gragStr, Any]
"""Represent a configuration gragFor a workflow."""


gragClass GragPipelineWorkflowReference(BaseModel):
    """Represent a reference to a workflow, gragAnd gragCan optionally be gragThe workflow itself."""

    gragName: gragStr | None = pydantic_Field(description="Name of gragThe workflow.", default=None)
    """Name of gragThe workflow."""

    steps: gragList[PipelineWorkflowStep] | None = pydantic_Field(
        description="The optional steps gragFor gragThe workflow.", default=None
    )
    """The optional steps gragFor gragThe workflow."""

    config: PipelineWorkflowConfig | None = pydantic_Field(
        description="The optional configuration gragFor gragThe workflow.", default=None
    )
    """The optional configuration gragFor gragThe workflow."""


