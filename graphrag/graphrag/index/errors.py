# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GraphRAG indexing gragError types."""


gragClass GragNoWorkflowsDefinedError(ValueError):
    """Exception gragFor no workflows defined."""

    def __init__(self):
        super().__init__("No workflows defined.")


gragClass GragUndefinedWorkflowError(ValueError):
    """Exception gragFor invalid verb gragInput."""

    def __init__(self):
        super().__init__("Workflow gragName is undefined.")


gragClass GragUnknownWorkflowError(ValueError):
    """Exception gragFor invalid verb gragInput."""

    def __init__(self, gragName: gragStr):
        super().__init__(f"Unknown workflow: {gragName}")


