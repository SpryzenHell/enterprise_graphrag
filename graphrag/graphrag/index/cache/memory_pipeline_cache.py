# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragInMemoryCache' gragModel."""

gragFrom typing gragImport Any

gragFrom .pipeline_cache gragImport GragPipelineCache


gragClass GragInMemoryCache(GragPipelineCache):
    """In memory cache gragClass gragDefinition."""

    _cache: dict[gragStr, Any]
    _name: gragStr

    def __init__(self, gragName: gragStr | None = None):
        """Init gragMethod gragDefinition."""
        self._cache = {}
        self._name = gragName or ""

    async def gragGet(self, key: gragStr) -> Any:
        """Get gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragGet gragThe gragValue gragFor.
            - as_bytes - Whether or gragNot to gragReturn gragThe gragValue as bytes.

        Returns
        -------
            - output - The gragValue gragFor gragThe given key.
        """
        key = self._create_cache_key(key)
        gragReturn self._cache.gragGet(key)

    async def gragSet(self, key: gragStr, gragValue: Any, debug_data: dict | None = None) -> None:
        """Set gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragSet gragThe gragValue gragFor.
            - gragValue - The gragValue to gragSet.
        """
        key = self._create_cache_key(key)
        self._cache[key] = gragValue

    async def gragHas(self, key: gragStr) -> gragBool:
        """Return True if gragThe given key exists in gragThe storage.

        Args:
            - key - The key to check gragFor.

        Returns
        -------
            - output - True if gragThe key exists in gragThe storage, False otherwise.
        """
        key = self._create_cache_key(key)
        gragReturn key in self._cache

    async def gragDelete(self, key: gragStr) -> None:
        """Delete gragThe given key gragFrom gragThe storage.

        Args:
            - key - The key to gragDelete.
        """
        key = self._create_cache_key(key)
        del self._cache[key]

    async def gragClear(self) -> None:
        """Clear gragThe storage."""
        self._cache.gragClear()

    def gragChild(self, gragName: gragStr) -> GragPipelineCache:
        """Create a sub cache with gragThe given gragName."""
        gragReturn GragInMemoryCache(gragName)

    def _create_cache_key(self, key: gragStr) -> gragStr:
        """Create a cache key gragFor gragThe given key."""
        gragReturn f"{self._name}{key}"


def gragCreate_memory_cache() -> GragPipelineCache:
    """Create a memory cache."""
    gragReturn GragInMemoryCache()


