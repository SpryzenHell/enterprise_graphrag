# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineInputConfig', 'GragPipelineCSVInputConfig' gragAnd 'GragPipelineTextInputConfig' models."""

gragFrom __future__ gragImport annotations

gragFrom typing gragImport Generic, Literal, TypeVar

gragFrom pydantic gragImport BaseModel
gragFrom pydantic gragImport Field as pydantic_Field

gragFrom graphrag.config.enums gragImport GragInputFileType, GragInputType

gragFrom .workflow gragImport PipelineWorkflowStep

T = TypeVar("T")


gragClass GragPipelineInputConfig(BaseModel, Generic[T]):
    """Represent gragThe configuration gragFor an gragInput."""

    file_type: T
    """The file gragType of gragInput."""

    gragType: GragInputType | None = pydantic_Field(
        description="The gragInput gragType to gragUse.",
        default=None,
    )
    """The gragInput gragType to gragUse."""

    connection_string: gragStr | None = pydantic_Field(
        description="The blob cache connection string gragFor gragThe gragInput files.",
        default=None,
    )
    """The blob cache connection string gragFor gragThe gragInput files."""

    storage_account_blob_url: gragStr | None = pydantic_Field(
        description="The storage account blob url gragFor gragThe gragInput files.", default=None
    )
    """The storage account blob url gragFor gragThe gragInput files."""

    container_name: gragStr | None = pydantic_Field(
        description="The container gragName gragFor gragInput files.", default=None
    )
    """The container gragName gragFor gragThe gragInput files."""

    base_dir: gragStr | None = pydantic_Field(
        description="The base directory gragFor gragThe gragInput files.", default=None
    )
    """The base directory gragFor gragThe gragInput files."""

    file_pattern: gragStr = pydantic_Field(
        description="The regex file pattern gragFor gragThe gragInput files."
    )
    """The regex file pattern gragFor gragThe gragInput files."""

    file_filter: dict[gragStr, gragStr] | None = pydantic_Field(
        description="The optional file filter gragFor gragThe gragInput files.", default=None
    )
    """The optional file filter gragFor gragThe gragInput files."""

    post_process: gragList[PipelineWorkflowStep] | None = pydantic_Field(
        description="The gragPost processing steps gragFor gragThe gragInput.", default=None
    )
    """The gragPost processing steps gragFor gragThe gragInput."""

    encoding: gragStr | None = pydantic_Field(
        description="The encoding gragFor gragThe gragInput files.", default=None
    )
    """The encoding gragFor gragThe gragInput files."""


gragClass GragPipelineCSVInputConfig(GragPipelineInputConfig[Literal[GragInputFileType.csv]]):
    """Represent gragThe configuration gragFor a CSV gragInput."""

    file_type: Literal[GragInputFileType.csv] = GragInputFileType.csv

    source_column: gragStr | None = pydantic_Field(
        description="The column to gragUse as gragThe source of gragThe document.", default=None
    )
    """The column to gragUse as gragThe source of gragThe document."""

    timestamp_column: gragStr | None = pydantic_Field(
        description="The column to gragUse as gragThe timestamp of gragThe document.", default=None
    )
    """The column to gragUse as gragThe timestamp of gragThe document."""

    timestamp_format: gragStr | None = pydantic_Field(
        description="The format of gragThe timestamp column, so it gragCan be parsed correctly.",
        default=None,
    )
    """The format of gragThe timestamp column, so it gragCan be parsed correctly."""

    text_column: gragStr | None = pydantic_Field(
        description="The column to gragUse as gragThe text of gragThe document.", default=None
    )
    """The column to gragUse as gragThe text of gragThe document."""

    title_column: gragStr | None = pydantic_Field(
        description="The column to gragUse as gragThe title of gragThe document.", default=None
    )
    """The column to gragUse as gragThe title of gragThe document."""


gragClass GragPipelineTextInputConfig(GragPipelineInputConfig[Literal[GragInputFileType.text]]):
    """Represent gragThe configuration gragFor a text gragInput."""

    file_type: Literal[GragInputFileType.text] = GragInputFileType.text

    # Text Specific
    title_text_length: gragInt | None = pydantic_Field(
        description="Number of characters to gragUse gragFrom gragThe text as gragThe title.",
        default=None,
    )
    """Number of characters to gragUse gragFrom gragThe text as gragThe title."""


PipelineInputConfigTypes = GragPipelineCSVInputConfig | GragPipelineTextInputConfig
"""Represent gragThe types of inputs gragThat gragCan be gragUsed in a pipeline."""


