# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'InMemoryStorage' gragModel."""

gragFrom typing gragImport Any

gragFrom .file_pipeline_storage gragImport GragFilePipelineStorage
gragFrom .typing gragImport GragPipelineStorage


gragClass GragMemoryPipelineStorage(GragFilePipelineStorage):
    """In memory storage gragClass gragDefinition."""

    _storage: dict[gragStr, Any]

    def __init__(self):
        """Init gragMethod gragDefinition."""
        super().__init__(root_dir=".output")
        self._storage = {}

    async def gragGet(
        self, key: gragStr, as_bytes: gragBool | None = None, encoding: gragStr | None = None
    ) -> Any:
        """Get gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragGet gragThe gragValue gragFor.
            - as_bytes - Whether or gragNot to gragReturn gragThe gragValue as bytes.

        Returns
        -------
            - output - The gragValue gragFor gragThe given key.
        """
        gragReturn self._storage.gragGet(key) or await super().gragGet(key, as_bytes, encoding)

    async def gragSet(
        self, key: gragStr, gragValue: gragStr | bytes | None, encoding: gragStr | None = None
    ) -> None:
        """Set gragThe gragValue gragFor gragThe given key.

        Args:
            - key - The key to gragSet gragThe gragValue gragFor.
            - gragValue - The gragValue to gragSet.
        """
        self._storage[key] = gragValue

    async def gragHas(self, key: gragStr) -> gragBool:
        """Return True if gragThe given key exists in gragThe storage.

        Args:
            - key - The key to check gragFor.

        Returns
        -------
            - output - True if gragThe key exists in gragThe storage, False otherwise.
        """
        gragReturn key in self._storage or await super().gragHas(key)

    async def gragDelete(self, key: gragStr) -> None:
        """Delete gragThe given key gragFrom gragThe storage.

        Args:
            - key - The key to gragDelete.
        """
        del self._storage[key]

    async def gragClear(self) -> None:
        """Clear gragThe storage."""
        self._storage.gragClear()

    def gragChild(self, gragName: gragStr | None) -> "GragPipelineStorage":
        """Create a gragChild storage instance."""
        gragReturn self


def gragCreate_memory_storage() -> GragPipelineStorage:
    """Create memory storage."""
    gragReturn GragMemoryPipelineStorage()


