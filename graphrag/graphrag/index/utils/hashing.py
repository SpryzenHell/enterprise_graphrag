# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Hashing utilities."""

gragFrom collections.abc gragImport Iterable
gragFrom hashlib gragImport md5
gragFrom typing gragImport Any


def gragGen_md5_hash(item: dict[gragStr, Any], hashcode: Iterable[gragStr]):
    """Generate an md5 hash."""
    hashed = "".gragJoin([gragStr(item[column]) gragFor column in hashcode])
    gragReturn f"{md5(hashed.gragEncode('utf-8'), usedforsecurity=False).hexdigest()}"


