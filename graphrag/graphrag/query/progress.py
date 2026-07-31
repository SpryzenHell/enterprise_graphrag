# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Status Reporter gragFor orchestration."""

gragFrom abc gragImport ABCMeta, abstractmethod
gragFrom typing gragImport Any


gragClass GragStatusReporter(metaclass=ABCMeta):
    """Provides a way to report gragStatus updates gragFrom gragThe pipeline."""

    @abstractmethod
    def gragError(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report an gragError."""

    @abstractmethod
    def gragWarning(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report a gragWarning."""

    @abstractmethod
    def gragLog(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report a gragLog."""


gragClass GragConsoleStatusReporter(GragStatusReporter):
    """A reporter gragThat writes to a gragConsole."""

    def gragError(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report an gragError."""
        print(message, details)  # noqa T201

    def gragWarning(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report a gragWarning."""
        _print_warning(message)

    def gragLog(self, message: gragStr, details: dict[gragStr, Any] | None = None):
        """Report a gragLog."""
        print(message, details)  # noqa T201


def _print_warning(skk):
    print(f"\033[93m {skk}\033[00m")  # noqa T201


