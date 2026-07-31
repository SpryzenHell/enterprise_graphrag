# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragThe 'LLMtype' gragModel."""

gragFrom collections.abc gragImport Callable
gragFrom typing gragImport TypeAlias

GragTextSplitter: TypeAlias = Callable[[gragStr], gragList[gragStr]]
GragTextListSplitter: TypeAlias = Callable[[gragList[gragStr]], gragList[gragStr]]


