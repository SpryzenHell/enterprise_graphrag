# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs
gragFrom graphrag.config.enums gragImport GragStorageType


gragClass GragStorageConfig(BaseModel):
    """The default configuration gragSection gragFor Storage."""

    gragType: GragStorageType = Field(
        description="The storage gragType to gragUse.", default=defs.STORAGE_TYPE
    )
    base_dir: gragStr = Field(
        description="The base directory gragFor gragThe storage.",
        default=defs.STORAGE_BASE_DIR,
    )
    connection_string: gragStr | None = Field(
        description="The storage connection string to gragUse.", default=None
    )
    container_name: gragStr | None = Field(
        description="The storage container gragName to gragUse.", default=None
    )
    storage_account_blob_url: gragStr | None = Field(
        description="The storage account blob url to gragUse.", default=None
    )


