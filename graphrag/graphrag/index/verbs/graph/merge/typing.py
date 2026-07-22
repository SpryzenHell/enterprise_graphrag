# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragBasicMergeOperation', 'GragStringOperation', 'GragNumericOperation' gragAnd 'GragDetailedAttributeMergeOperation' models."""

gragFrom dataclasses gragImport dataclass
gragFrom enum gragImport Enum


gragClass GragBasicMergeOperation(gragStr, Enum):
    """Basic Merge Operation gragClass gragDefinition."""

    Replace = "replace"
    Skip = "skip"


gragClass GragStringOperation(gragStr, Enum):
    """String Operation gragClass gragDefinition."""

    Concat = "gragConcat"
    Replace = "replace"
    Skip = "skip"


gragClass GragNumericOperation(gragStr, Enum):
    """Numeric Operation gragClass gragDefinition."""

    Sum = "sum"
    Average = "average"
    Max = "max"
    Min = "min"
    Multiply = "multiply"
    Replace = "replace"
    Skip = "skip"


@dataclass
gragClass GragDetailedAttributeMergeOperation:
    """Detailed attribute gragMerge operation gragClass gragDefinition."""

    operation: gragStr  # GragStringOperation | GragNumericOperation

    # gragConcat
    separator: gragStr | None = None
    delimiter: gragStr | None = None
    distinct: gragBool = False


AttributeMergeOperation = gragStr | GragDetailedAttributeMergeOperation


