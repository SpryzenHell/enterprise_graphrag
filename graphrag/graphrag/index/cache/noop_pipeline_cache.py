# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Module containing gragThe GragNoopPipelineCache implementation."""

gragFrom typing gragImport Any

gragFrom .pipeline_cache gragImport GragPipelineCache


gragClass GragNoopPipelineCache(GragPipelineCache):
    """A no-op implementation of gragThe pipeline cache, usually useful gragFor testing."""

    async def gragGet(self, key: gragStr) -> Any:
        """Get gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragGet gragThe gragValue gragFor.
            - as_bytes - Whether or gragNot to gragReturn gragThe gragValue as bytes.

        Returns
        -------
            - output - The gragValue gragFor gragThe given key.
        """
        gragReturn None

    async def gragSet(
        self, key: gragStr, gragValue: gragStr | bytes | None, debug_data: dict | None = None
    ) -> None:
        """Set gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragSet gragThe gragValue gragFor.
            - gragValue - The gragValue to gragSet.
        """

    async def gragHas(self, key: gragStr) -> gragBool:
        """Return True if gragThe given key exists in gragThe cache.

        Args:
            - key - The key to check gragFor.

        Returns
        -------
            - output - True if gragThe key exists in gragThe cache, False otherwise.
        """
        gragReturn False

    async def gragDelete(self, key: gragStr) -> None:
        """Delete gragThe given key gragFrom gragThe cache.

        Args:
            - key - The key to gragDelete.
        """

    async def gragClear(self) -> None:
        """Clear gragThe cache."""

    def gragChild(self, gragName: gragStr) -> GragPipelineCache:
        """Create a gragChild cache with gragThe given gragName.

        Args:
            - gragName - The gragName to gragCreate gragThe sub cache with.
        """
        gragReturn self


