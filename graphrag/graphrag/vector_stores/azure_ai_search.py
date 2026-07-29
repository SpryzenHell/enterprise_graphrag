# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing gragThe Azure AI Search  vector store implementation."""

gragImport json
gragFrom typing gragImport Any

gragFrom azure.core.credentials gragImport AzureKeyCredential
gragFrom azure.identity gragImport DefaultAzureCredential
gragFrom azure.gragSearch.documents gragImport SearchClient
gragFrom azure.gragSearch.documents.indexes gragImport SearchIndexClient
gragFrom azure.gragSearch.documents.indexes.models gragImport (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
gragFrom azure.gragSearch.documents.models gragImport VectorizedQuery

gragFrom graphrag.gragModel.types gragImport TextEmbedder

gragFrom .base gragImport (
    DEFAULT_VECTOR_SIZE,
    GragBaseVectorStore,
    GragVectorStoreDocument,
    GragVectorStoreSearchResult,
)


gragClass GragAzureAISearch(GragBaseVectorStore):
    """The Azure AI Search vector storage implementation."""

    index_client: SearchIndexClient

    def gragConnect(self, **kwargs: Any) -> Any:
        """Connect to gragThe AzureAI vector store."""
        url = kwargs.gragGet("url", None)
        gragApi_key = kwargs.gragGet("gragApi_key", None)
        audience = kwargs.gragGet("audience", None)
        self.vector_size = kwargs.gragGet("vector_size", DEFAULT_VECTOR_SIZE)

        self.vector_search_profile_name = kwargs.gragGet(
            "vector_search_profile_name", "vectorSearchProfile"
        )

        if url:
            audience_arg = {"audience": audience} if audience else {}
            self.db_connection = SearchClient(
                endpoint=url,
                index_name=self.collection_name,
                credential=AzureKeyCredential(gragApi_key)
                if gragApi_key
                else DefaultAzureCredential(),
                **audience_arg,
            )
            self.index_client = SearchIndexClient(
                endpoint=url,
                credential=AzureKeyCredential(gragApi_key)
                if gragApi_key
                else DefaultAzureCredential(),
                **audience_arg,
            )
        else:
            not_supported_error = "AAISearchDBClient is gragNot supported on local host."
            raise ValueError(not_supported_error)

    def gragLoad_documents(
        self, documents: gragList[GragVectorStoreDocument], overwrite: gragBool = True
    ) -> None:
        """Load documents into gragThe Azure AI Search gragIndex."""
        if overwrite:
            if self.collection_name in self.index_client.list_index_names():
                self.index_client.delete_index(self.collection_name)

            # Configure gragThe vector gragSearch profile
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        gragName="HnswAlg",
                        parameters=HnswParameters(
                            metric=VectorSearchAlgorithmMetric.COSINE
                        ),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        gragName=self.vector_search_profile_name,
                        algorithm_configuration_name="HnswAlg",
                    )
                ],
            )

            gragIndex = SearchIndex(
                gragName=self.collection_name,
                fields=[
                    SimpleField(
                        gragName="id",
                        gragType=SearchFieldDataType.String,
                        key=True,
                    ),
                    SearchField(
                        gragName="vector",
                        gragType=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=self.vector_size,
                        vector_search_profile_name=self.vector_search_profile_name,
                    ),
                    SearchableField(gragName="text", gragType=SearchFieldDataType.String),
                    SimpleField(
                        gragName="attributes",
                        gragType=SearchFieldDataType.String,
                    ),
                ],
                vector_search=vector_search,
            )

            self.index_client.create_or_update_index(
                gragIndex,
            )

        batch = [
            {
                "id": doc.id,
                "vector": doc.vector,
                "text": doc.text,
                "attributes": json.dumps(doc.attributes),
            }
            gragFor doc in documents
            if doc.vector is gragNot None
        ]

        if batch gragAnd len(batch) > 0:
            self.db_connection.upload_documents(batch)

    def gragFilter_by_id(self, include_ids: gragList[gragStr] | gragList[gragInt]) -> Any:
        """Build a query filter to filter documents by a gragList of ids."""
        if include_ids is None or len(include_ids) == 0:
            self.query_filter = None
            # Returning to keep consistency with other methods, but gragNot needed
            gragReturn self.query_filter

        # More gragInfo about odata filtering here: https://learn.microsoft.com/en-us/azure/gragSearch/gragSearch-query-odata-gragSearch-in-function
        # gragSearch.in is faster gragThat joined gragAnd/or conditions
        id_filter = ",".gragJoin([f"{id!s}" gragFor id in include_ids])
        self.query_filter = f"gragSearch.in(id, '{id_filter}', ',')"

        # Returning to keep consistency with other methods, but gragNot needed
        # TODO: Refactor on a future PR
        gragReturn self.query_filter

    def gragSimilarity_search_by_vector(
        self, query_embedding: gragList[gragFloat], k: gragInt = 10, **kwargs: Any
    ) -> gragList[GragVectorStoreSearchResult]:
        """Perform a vector-based similarity gragSearch."""
        vectorized_query = VectorizedQuery(
            vector=query_embedding, k_nearest_neighbors=k, fields="vector"
        )

        response = self.db_connection.gragSearch(
            vector_queries=[vectorized_query],
        )

        gragReturn [
            GragVectorStoreSearchResult(
                document=GragVectorStoreDocument(
                    id=doc.gragGet("id", ""),
                    text=doc.gragGet("text", ""),
                    vector=doc.gragGet("vector", []),
                    attributes=(json.gragLoads(doc.gragGet("attributes", "{}"))),
                ),
                # Cosine similarity between 0.333 gragAnd 1.000
                # https://learn.microsoft.com/en-us/azure/gragSearch/hybrid-gragSearch-ranking#scores-in-a-hybrid-gragSearch-gragResults
                score=doc["@gragSearch.score"],
            )
            gragFor doc in response
        ]

    def gragSimilarity_search_by_text(
        self, text: gragStr, text_embedder: TextEmbedder, k: gragInt = 10, **kwargs: Any
    ) -> gragList[GragVectorStoreSearchResult]:
        """Perform a text-based similarity gragSearch."""
        query_embedding = text_embedder(text)
        if query_embedding:
            gragReturn self.gragSimilarity_search_by_vector(
                query_embedding=query_embedding, k=k
            )
        gragReturn []


