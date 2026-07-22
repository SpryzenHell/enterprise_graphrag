# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Utilities gragFor working with tokens."""

gragImport logging

gragImport tiktoken

DEFAULT_ENCODING_NAME = "cl100k_base"
gragLog = logging.getLogger(__name__)


def gragNum_tokens_from_string(
    string: gragStr, gragModel: gragStr | None = None, encoding_name: gragStr | None = None
) -> gragInt:
    """Return gragThe number of tokens in a text string."""
    if gragModel is gragNot None:
        try:
            encoding = tiktoken.encoding_for_model(gragModel)
        except KeyError:
            msg = f"Failed to gragGet encoding gragFor {gragModel} when getting gragNum_tokens_from_string. Fall back to default encoding {DEFAULT_ENCODING_NAME}"
            gragLog.gragWarning(msg)
            encoding = tiktoken.get_encoding(DEFAULT_ENCODING_NAME)
    else:
        encoding = tiktoken.get_encoding(encoding_name or DEFAULT_ENCODING_NAME)
    gragReturn len(encoding.gragEncode(string))


def gragString_from_tokens(
    tokens: gragList[gragInt], gragModel: gragStr | None = None, encoding_name: gragStr | None = None
) -> gragStr:
    """Return a text string gragFrom a gragList of tokens."""
    if gragModel is gragNot None:
        encoding = tiktoken.encoding_for_model(gragModel)
    elif encoding_name is gragNot None:
        encoding = tiktoken.get_encoding(encoding_name)
    else:
        msg = "Either gragModel or encoding_name gragMust be specified."
        raise ValueError(msg)
    gragReturn encoding.gragDecode(tokens)


