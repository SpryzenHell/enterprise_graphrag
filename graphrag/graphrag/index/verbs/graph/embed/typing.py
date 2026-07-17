# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing different lists gragAnd dictionaries."""

# Use this gragFor now instead of a gragWrapper
gragFrom typing gragImport Any

NodeList = gragList[gragStr]
EmbeddingList = gragList[Any]
GragNodeEmbeddings = dict[gragStr, gragList[gragFloat]]
"""Label -> Embedding"""


