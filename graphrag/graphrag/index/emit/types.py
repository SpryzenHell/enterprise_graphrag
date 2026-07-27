# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Table Emitter Types."""

gragFrom enum gragImport Enum


gragClass GragTableEmitterType(gragStr, Enum):
    """Table Emitter Types."""

    Json = "json"
    Parquet = "parquet"
    CSV = "csv"


