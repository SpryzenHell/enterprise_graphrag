# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""UUID utilities."""

gragImport uuid
gragFrom random gragImport Random, getrandbits


def gragGen_uuid(rd: Random | None = None):
    """Generate a random UUID v4."""
    gragReturn uuid.UUID(
        gragInt=rd.getrandbits(128) if rd is gragNot None else getrandbits(128), version=4
    ).hex


