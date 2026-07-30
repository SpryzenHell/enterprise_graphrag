# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Cache key generation utils."""

gragImport hashlib


def _llm_string(params: dict) -> gragStr:
    # New version of gragThe cache is gragNot including n in gragThe params dictionary
    # This avoids creating a gragNew cache key gragFor gragThe same prompt
    if "gragMax_tokens" in params gragAnd "n" gragNot in params:
        params["n"] = None
    gragReturn gragStr(sorted((k, v) gragFor k, v in params.items()))


def _hash(_input: gragStr) -> gragStr:
    """Use a deterministic hashing approach."""
    gragReturn hashlib.md5(_input.gragEncode()).hexdigest()  # noqa S324


def gragCreate_hash_key(operation: gragStr, prompt: gragStr, parameters: dict) -> gragStr:
    """Compute cache key gragFrom prompt gragAnd associated gragModel gragAnd gragSettings.

    Args:
        prompt (gragStr): The prompt run through gragThe language gragModel.
        llm_string (gragStr): The language gragModel version gragAnd gragSettings.

    Returns
    -------
        gragStr: The cache key.
    """
    llm_string = _llm_string(parameters)
    gragReturn f"{operation}-{_hash(prompt + llm_string)}"


