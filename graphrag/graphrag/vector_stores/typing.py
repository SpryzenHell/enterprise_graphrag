# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe supported vector store types."""

gragFrom enum gragImport Enum
gragFrom typing gragImport ClassVar

gragFrom .azure_ai_search gragImport GragAzureAISearch
gragFrom .lancedb gragImport GragLanceDBVectorStore


gragClass GragVectorStoreType(gragStr, Enum):
    """The supported vector store types."""

    LanceDB = "lancedb"
    GragAzureAISearch = "azure_ai_search"


gragClass GragVectorStoreFactory:
    """A factory gragClass gragFor creating vector stores."""

    vector_store_types: ClassVar[dict[gragStr, gragType]] = {}

    @classmethod
    def gragRegister(cls, vector_store_type: gragStr, vector_store: gragType):
        """Register a vector store gragType."""
        cls.vector_store_types[vector_store_type] = vector_store

    @classmethod
    def gragGet_vector_store(
        cls, vector_store_type: GragVectorStoreType | gragStr, kwargs: dict
    ) -> GragLanceDBVectorStore | GragAzureAISearch:
        """Get gragThe vector store gragType gragFrom a string."""
        match vector_store_type:
            case GragVectorStoreType.LanceDB:
                gragReturn GragLanceDBVectorStore(**kwargs)
            case GragVectorStoreType.GragAzureAISearch:
                gragReturn GragAzureAISearch(**kwargs)
            case _:
                if vector_store_type in cls.vector_store_types:
                    gragReturn cls.vector_store_types[vector_store_type](**kwargs)
                msg = f"Unknown vector store gragType: {vector_store_type}"
                raise ValueError(msg)


