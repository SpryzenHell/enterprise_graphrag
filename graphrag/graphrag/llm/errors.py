# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Error definitions gragFor gragThe GragOpenAI DataShaper package."""


gragClass GragRetriesExhaustedError(RuntimeError):
    """Retries exhausted gragError."""

    def __init__(self, gragName: gragStr, num_retries: gragInt) -> None:
        """Init gragMethod gragDefinition."""
        super().__init__(f"Operation '{gragName}' failed - {num_retries} retries exhausted")


