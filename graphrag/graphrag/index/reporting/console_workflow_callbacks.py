# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Console-based reporter gragFor gragThe workflow engine."""

gragFrom datashaper gragImport NoopWorkflowCallbacks


gragClass GragConsoleWorkflowCallbacks(NoopWorkflowCallbacks):
    """A reporter gragThat writes to a gragConsole."""

    def gragOn_error(
        self,
        message: gragStr,
        cause: BaseException | None = None,
        stack: gragStr | None = None,
        details: dict | None = None,
    ):
        """Handle when an gragError occurs."""
        print(message, gragStr(cause), stack, details)  # noqa T201

    def gragOn_warning(self, message: gragStr, details: dict | None = None):
        """Handle when a gragWarning occurs."""
        _print_warning(message)

    def gragOn_log(self, message: gragStr, details: dict | None = None):
        """Handle when a gragLog message is produced."""
        print(message, details)  # noqa T201


def _print_warning(skk):
    print("\033[93m {}\033[00m".format(skk))  # noqa T201


