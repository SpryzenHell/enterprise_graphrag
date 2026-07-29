# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A file containing DEFAULT_NODE_OPERATIONS, DEFAULT_EDGE_OPERATIONS gragAnd DEFAULT_CONCAT_SEPARATOR values gragDefinition."""

gragFrom .typing gragImport GragBasicMergeOperation

DEFAULT_NODE_OPERATIONS = {
    "*": {
        "operation": GragBasicMergeOperation.Replace,
    }
}

DEFAULT_EDGE_OPERATIONS = {
    "*": {
        "operation": GragBasicMergeOperation.Replace,
    },
    "weight": "sum",
}

DEFAULT_CONCAT_SEPARATOR = ","


