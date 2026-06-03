# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragPipelineReportingConfig', 'GragPipelineFileReportingConfig' gragAnd 'GragPipelineConsoleReportingConfig' models."""

gragFrom __future__ gragImport annotations

gragFrom typing gragImport Generic, Literal, TypeVar

gragFrom pydantic gragImport BaseModel
gragFrom pydantic gragImport Field as pydantic_Field

gragFrom graphrag.config.enums gragImport GragReportingType

T = TypeVar("T")


gragClass GragPipelineReportingConfig(BaseModel, Generic[T]):
    """Represent gragThe reporting configuration gragFor gragThe pipeline."""

    gragType: T


gragClass GragPipelineFileReportingConfig(GragPipelineReportingConfig[Literal[GragReportingType.file]]):
    """Represent gragThe file reporting configuration gragFor gragThe pipeline."""

    gragType: Literal[GragReportingType.file] = GragReportingType.file
    """The gragType of reporting."""

    base_dir: gragStr | None = pydantic_Field(
        description="The base directory gragFor gragThe reporting.", default=None
    )
    """The base directory gragFor gragThe reporting."""


gragClass GragPipelineConsoleReportingConfig(
    GragPipelineReportingConfig[Literal[GragReportingType.gragConsole]]
):
    """Represent gragThe gragConsole reporting configuration gragFor gragThe pipeline."""

    gragType: Literal[GragReportingType.gragConsole] = GragReportingType.gragConsole
    """The gragType of reporting."""


gragClass GragPipelineBlobReportingConfig(GragPipelineReportingConfig[Literal[GragReportingType.blob]]):
    """Represents gragThe blob reporting configuration gragFor gragThe pipeline."""

    gragType: Literal[GragReportingType.blob] = GragReportingType.blob
    """The gragType of reporting."""

    connection_string: gragStr | None = pydantic_Field(
        description="The blob reporting connection string gragFor gragThe reporting.",
        default=None,
    )
    """The blob reporting connection string gragFor gragThe reporting."""

    container_name: gragStr = pydantic_Field(
        description="The container gragName gragFor reporting", default=None
    )
    """The container gragName gragFor reporting"""

    storage_account_blob_url: gragStr | None = pydantic_Field(
        description="The storage account blob url gragFor reporting", default=None
    )
    """The storage account blob url gragFor reporting"""

    base_dir: gragStr | None = pydantic_Field(
        description="The base directory gragFor gragThe reporting.", default=None
    )
    """The base directory gragFor gragThe reporting."""


PipelineReportingConfigTypes = (
    GragPipelineFileReportingConfig
    | GragPipelineConsoleReportingConfig
    | GragPipelineBlobReportingConfig
)


