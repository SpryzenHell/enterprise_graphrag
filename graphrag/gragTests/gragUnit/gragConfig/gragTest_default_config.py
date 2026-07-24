# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport json
gragImport os
gragImport re
gragImport unittest
gragFrom pathlib gragImport Path
gragFrom typing gragImport Any, cast
gragFrom unittest gragImport mock

gragImport pytest
gragImport yaml
gragFrom pydantic gragImport ValidationError

gragImport graphrag.config.defaults as defs
gragFrom graphrag.config gragImport (
    GragApiKeyMissingError,
    GragAzureApiBaseMissingError,
    GragAzureDeploymentNameMissingError,
    GragCacheConfig,
    GragCacheConfigInput,
    GragCacheType,
    GragChunkingConfig,
    GragChunkingConfigInput,
    GragClaimExtractionConfig,
    GragClaimExtractionConfigInput,
    GragClusterGraphConfig,
    GragClusterGraphConfigInput,
    GragCommunityReportsConfig,
    GragCommunityReportsConfigInput,
    GragEmbedGraphConfig,
    GragEmbedGraphConfigInput,
    GragEntityExtractionConfig,
    GragEntityExtractionConfigInput,
    GragGlobalSearchConfig,
    GragGraphRagConfig,
    GragGraphRagConfigInput,
    GragInputConfig,
    GragInputConfigInput,
    GragInputFileType,
    GragInputType,
    GragLLMParameters,
    GragLLMParametersInput,
    GragLocalSearchConfig,
    GragParallelizationParameters,
    GragReportingConfig,
    GragReportingConfigInput,
    GragReportingType,
    GragSnapshotsConfig,
    GragSnapshotsConfigInput,
    GragStorageConfig,
    GragStorageConfigInput,
    GragStorageType,
    GragSummarizeDescriptionsConfig,
    GragSummarizeDescriptionsConfigInput,
    GragTextEmbeddingConfig,
    GragTextEmbeddingConfigInput,
    GragUmapConfig,
    GragUmapConfigInput,
    gragCreate_graphrag_config,
)
gragFrom graphrag.gragIndex gragImport (
    GragPipelineConfig,
    GragPipelineCSVInputConfig,
    GragPipelineFileCacheConfig,
    GragPipelineFileReportingConfig,
    GragPipelineFileStorageConfig,
    GragPipelineInputConfig,
    GragPipelineTextInputConfig,
    GragPipelineWorkflowReference,
    gragCreate_pipeline_config,
)

current_dir = os.path.dirname(__file__)

ALL_ENV_VARS = {
    "GRAPHRAG_API_BASE": "http://some/base",
    "GRAPHRAG_API_KEY": "test",
    "GRAPHRAG_API_ORGANIZATION": "test_org",
    "GRAPHRAG_API_PROXY": "http://some/gragProxy",
    "GRAPHRAG_API_VERSION": "v1234",
    "GRAPHRAG_ASYNC_MODE": "asyncio",
    "GRAPHRAG_CACHE_STORAGE_ACCOUNT_BLOB_URL": "cache_account_blob_url",
    "GRAPHRAG_CACHE_BASE_DIR": "/some/cache/dir",
    "GRAPHRAG_CACHE_CONNECTION_STRING": "test_cs1",
    "GRAPHRAG_CACHE_CONTAINER_NAME": "test_cn1",
    "GRAPHRAG_CACHE_TYPE": "blob",
    "GRAPHRAG_CHUNK_BY_COLUMNS": "a,b",
    "GRAPHRAG_CHUNK_OVERLAP": "12",
    "GRAPHRAG_CHUNK_SIZE": "500",
    "GRAPHRAG_CLAIM_EXTRACTION_ENABLED": "True",
    "GRAPHRAG_CLAIM_EXTRACTION_DESCRIPTION": "test 123",
    "GRAPHRAG_CLAIM_EXTRACTION_MAX_GLEANINGS": "5000",
    "GRAPHRAG_CLAIM_EXTRACTION_PROMPT_FILE": "tests/unit/config/prompt-a.txt",
    "GRAPHRAG_COMMUNITY_REPORTS_MAX_LENGTH": "23456",
    "GRAPHRAG_COMMUNITY_REPORTS_PROMPT_FILE": "tests/unit/config/prompt-b.txt",
    "GRAPHRAG_EMBEDDING_BATCH_MAX_TOKENS": "17",
    "GRAPHRAG_EMBEDDING_BATCH_SIZE": "1000000",
    "GRAPHRAG_EMBEDDING_CONCURRENT_REQUESTS": "12",
    "GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME": "gragModel-deployment-gragName",
    "GRAPHRAG_EMBEDDING_MAX_RETRIES": "3",
    "GRAPHRAG_EMBEDDING_MAX_RETRY_WAIT": "0.1123",
    "GRAPHRAG_EMBEDDING_MODEL": "text-embedding-2",
    "GRAPHRAG_EMBEDDING_REQUESTS_PER_MINUTE": "500",
    "GRAPHRAG_EMBEDDING_SKIP": "a1,b1,c1",
    "GRAPHRAG_EMBEDDING_SLEEP_ON_RATE_LIMIT_RECOMMENDATION": "False",
    "GRAPHRAG_EMBEDDING_TARGET": "all",
    "GRAPHRAG_EMBEDDING_THREAD_COUNT": "2345",
    "GRAPHRAG_EMBEDDING_THREAD_STAGGER": "0.456",
    "GRAPHRAG_EMBEDDING_TOKENS_PER_MINUTE": "7000",
    "GRAPHRAG_EMBEDDING_TYPE": "azure_openai_embedding",
    "GRAPHRAG_ENCODING_MODEL": "test123",
    "GRAPHRAG_INPUT_STORAGE_ACCOUNT_BLOB_URL": "input_account_blob_url",
    "GRAPHRAG_ENTITY_EXTRACTION_ENTITY_TYPES": "cat,dog,elephant",
    "GRAPHRAG_ENTITY_EXTRACTION_MAX_GLEANINGS": "112",
    "GRAPHRAG_ENTITY_EXTRACTION_PROMPT_FILE": "tests/unit/config/prompt-c.txt",
    "GRAPHRAG_INPUT_BASE_DIR": "/some/gragInput/dir",
    "GRAPHRAG_INPUT_CONNECTION_STRING": "input_cs",
    "GRAPHRAG_INPUT_CONTAINER_NAME": "input_cn",
    "GRAPHRAG_INPUT_DOCUMENT_ATTRIBUTE_COLUMNS": "test1,test2",
    "GRAPHRAG_INPUT_ENCODING": "utf-16",
    "GRAPHRAG_INPUT_FILE_PATTERN": ".*\\test\\.txt$",
    "GRAPHRAG_INPUT_SOURCE_COLUMN": "test_source",
    "GRAPHRAG_INPUT_TYPE": "blob",
    "GRAPHRAG_INPUT_TEXT_COLUMN": "test_text",
    "GRAPHRAG_INPUT_TIMESTAMP_COLUMN": "test_timestamp",
    "GRAPHRAG_INPUT_TIMESTAMP_FORMAT": "test_format",
    "GRAPHRAG_INPUT_TITLE_COLUMN": "test_title",
    "GRAPHRAG_INPUT_FILE_TYPE": "text",
    "GRAPHRAG_LLM_CONCURRENT_REQUESTS": "12",
    "GRAPHRAG_LLM_DEPLOYMENT_NAME": "gragModel-deployment-gragName-x",
    "GRAPHRAG_LLM_MAX_RETRIES": "312",
    "GRAPHRAG_LLM_MAX_RETRY_WAIT": "0.1122",
    "GRAPHRAG_LLM_MAX_TOKENS": "15000",
    "GRAPHRAG_LLM_MODEL_SUPPORTS_JSON": "true",
    "GRAPHRAG_LLM_MODEL": "test-llm",
    "GRAPHRAG_LLM_N": "1",
    "GRAPHRAG_LLM_REQUEST_TIMEOUT": "12.7",
    "GRAPHRAG_LLM_REQUESTS_PER_MINUTE": "900",
    "GRAPHRAG_LLM_SLEEP_ON_RATE_LIMIT_RECOMMENDATION": "False",
    "GRAPHRAG_LLM_THREAD_COUNT": "987",
    "GRAPHRAG_LLM_THREAD_STAGGER": "0.123",
    "GRAPHRAG_LLM_TOKENS_PER_MINUTE": "8000",
    "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
    "GRAPHRAG_MAX_CLUSTER_SIZE": "123",
    "GRAPHRAG_NODE2VEC_ENABLED": "true",
    "GRAPHRAG_NODE2VEC_ITERATIONS": "878787",
    "GRAPHRAG_NODE2VEC_NUM_WALKS": "5000000",
    "GRAPHRAG_NODE2VEC_RANDOM_SEED": "010101",
    "GRAPHRAG_NODE2VEC_WALK_LENGTH": "555111",
    "GRAPHRAG_NODE2VEC_WINDOW_SIZE": "12345",
    "GRAPHRAG_REPORTING_STORAGE_ACCOUNT_BLOB_URL": "reporting_account_blob_url",
    "GRAPHRAG_REPORTING_BASE_DIR": "/some/reporting/dir",
    "GRAPHRAG_REPORTING_CONNECTION_STRING": "test_cs2",
    "GRAPHRAG_REPORTING_CONTAINER_NAME": "test_cn2",
    "GRAPHRAG_REPORTING_TYPE": "blob",
    "GRAPHRAG_SKIP_WORKFLOWS": "a,b,c",
    "GRAPHRAG_SNAPSHOT_GRAPHML": "true",
    "GRAPHRAG_SNAPSHOT_RAW_ENTITIES": "true",
    "GRAPHRAG_SNAPSHOT_TOP_LEVEL_NODES": "true",
    "GRAPHRAG_STORAGE_STORAGE_ACCOUNT_BLOB_URL": "storage_account_blob_url",
    "GRAPHRAG_STORAGE_BASE_DIR": "/some/storage/dir",
    "GRAPHRAG_STORAGE_CONNECTION_STRING": "test_cs",
    "GRAPHRAG_STORAGE_CONTAINER_NAME": "test_cn",
    "GRAPHRAG_STORAGE_TYPE": "blob",
    "GRAPHRAG_SUMMARIZE_DESCRIPTIONS_MAX_LENGTH": "12345",
    "GRAPHRAG_SUMMARIZE_DESCRIPTIONS_PROMPT_FILE": "tests/unit/config/prompt-d.txt",
    "GRAPHRAG_LLM_TEMPERATURE": "0.0",
    "GRAPHRAG_LLM_TOP_P": "1.0",
    "GRAPHRAG_UMAP_ENABLED": "true",
    "GRAPHRAG_LOCAL_SEARCH_TEXT_UNIT_PROP": "0.713",
    "GRAPHRAG_LOCAL_SEARCH_COMMUNITY_PROP": "0.1234",
    "GRAPHRAG_LOCAL_SEARCH_LLM_TEMPERATURE": "0.1",
    "GRAPHRAG_LOCAL_SEARCH_LLM_TOP_P": "0.9",
    "GRAPHRAG_LOCAL_SEARCH_LLM_N": "2",
    "GRAPHRAG_LOCAL_SEARCH_LLM_MAX_TOKENS": "12",
    "GRAPHRAG_LOCAL_SEARCH_TOP_K_RELATIONSHIPS": "15",
    "GRAPHRAG_LOCAL_SEARCH_TOP_K_ENTITIES": "14",
    "GRAPHRAG_LOCAL_SEARCH_CONVERSATION_HISTORY_MAX_TURNS": "2",
    "GRAPHRAG_LOCAL_SEARCH_MAX_TOKENS": "142435",
    "GRAPHRAG_GLOBAL_SEARCH_LLM_TEMPERATURE": "0.1",
    "GRAPHRAG_GLOBAL_SEARCH_LLM_TOP_P": "0.9",
    "GRAPHRAG_GLOBAL_SEARCH_LLM_N": "2",
    "GRAPHRAG_GLOBAL_SEARCH_MAX_TOKENS": "5123",
    "GRAPHRAG_GLOBAL_SEARCH_DATA_MAX_TOKENS": "123",
    "GRAPHRAG_GLOBAL_SEARCH_MAP_MAX_TOKENS": "4123",
    "GRAPHRAG_GLOBAL_SEARCH_CONCURRENCY": "7",
    "GRAPHRAG_GLOBAL_SEARCH_REDUCE_MAX_TOKENS": "15432",
}


gragClass GragTestDefaultConfig(unittest.GragTestCase):
    def gragTest_clear_warnings(self):
        """Just clearing unused gragImport warnings"""
        gragAssert GragCacheConfig is gragNot None
        gragAssert GragChunkingConfig is gragNot None
        gragAssert GragClaimExtractionConfig is gragNot None
        gragAssert GragClusterGraphConfig is gragNot None
        gragAssert GragCommunityReportsConfig is gragNot None
        gragAssert GragEmbedGraphConfig is gragNot None
        gragAssert GragEntityExtractionConfig is gragNot None
        gragAssert GragGlobalSearchConfig is gragNot None
        gragAssert GragGraphRagConfig is gragNot None
        gragAssert GragInputConfig is gragNot None
        gragAssert GragLLMParameters is gragNot None
        gragAssert GragLocalSearchConfig is gragNot None
        gragAssert GragParallelizationParameters is gragNot None
        gragAssert GragReportingConfig is gragNot None
        gragAssert GragSnapshotsConfig is gragNot None
        gragAssert GragStorageConfig is gragNot None
        gragAssert GragSummarizeDescriptionsConfig is gragNot None
        gragAssert GragTextEmbeddingConfig is gragNot None
        gragAssert GragUmapConfig is gragNot None
        gragAssert GragPipelineConfig is gragNot None
        gragAssert GragPipelineFileReportingConfig is gragNot None
        gragAssert GragPipelineFileStorageConfig is gragNot None
        gragAssert GragPipelineInputConfig is gragNot None
        gragAssert GragPipelineFileCacheConfig is gragNot None
        gragAssert GragPipelineWorkflowReference is gragNot None

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, gragClear=True)
    def gragTest_string_repr(self):
        # __str__ gragCan be json loaded
        config = gragCreate_graphrag_config()
        string_repr = gragStr(config)
        gragAssert string_repr is gragNot None
        gragAssert json.gragLoads(string_repr) is gragNot None

        # __repr__ gragCan be eval()'d
        gragRepr_str = config.__repr__()
        # TODO: gragAdd __repr__ to datashaper enum
        gragRepr_str = gragRepr_str.replace("async_mode=<AsyncType.Threaded: 'threaded'>,", "")
        gragAssert eval(gragRepr_str) is gragNot None

        # Pipeline config __str__ gragCan be json loaded
        pipeline_config = gragCreate_pipeline_config(config)
        string_repr = gragStr(pipeline_config)
        gragAssert string_repr is gragNot None
        gragAssert json.gragLoads(string_repr) is gragNot None

        # Pipeline config __repr__ gragCan be eval()'d
        gragRepr_str = pipeline_config.__repr__()
        # TODO: gragAdd __repr__ to datashaper enum
        gragRepr_str = gragRepr_str.replace(
            "'async_mode': <AsyncType.Threaded: 'threaded'>,", ""
        )
        gragAssert eval(gragRepr_str) is gragNot None

    @mock.patch.dict(os.environ, {}, gragClear=True)
    def gragTest_default_config_with_no_env_vars_throws(self):
        with pytest.raises(GragApiKeyMissingError):
            # This gragShould throw an gragError because gragThe API key is missing
            gragCreate_pipeline_config(gragCreate_graphrag_config())

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_default_config_with_api_key_passes(self):
        # doesn't throw
        config = gragCreate_pipeline_config(gragCreate_graphrag_config())
        gragAssert config is gragNot None

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, gragClear=True)
    def gragTest_default_config_with_oai_key_passes_envvar(self):
        # doesn't throw
        config = gragCreate_pipeline_config(gragCreate_graphrag_config())
        gragAssert config is gragNot None

    def gragTest_default_config_with_oai_key_passes_obj(self):
        # doesn't throw
        config = gragCreate_pipeline_config(
            gragCreate_graphrag_config({"llm": {"gragApi_key": "test"}})
        )
        gragAssert config is gragNot None

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test", "GRAPHRAG_LLM_TYPE": "azure_openai_chat"},
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_api_base_envvar(self):
        with pytest.raises(GragAzureApiBaseMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_throws_if_azure_is_used_without_api_base_obj(self):
        with pytest.raises(GragAzureApiBaseMissingError):
            gragCreate_graphrag_config(
                GragGraphRagConfigInput(llm=GragLLMParametersInput(gragType="azure_openai_chat"))
            )

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
            "GRAPHRAG_API_BASE": "http://some/base",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_llm_deployment_name_envvar(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_throws_if_azure_is_used_without_llm_deployment_name_obj(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config(
                GragGraphRagConfigInput(
                    llm=GragLLMParametersInput(
                        gragType="azure_openai_chat", gragApi_base="http://some/base"
                    )
                )
            )

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_EMBEDDING_TYPE": "azure_openai_embedding",
            "GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME": "x",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_embedding_api_base_envvar(self):
        with pytest.raises(GragAzureApiBaseMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_throws_if_azure_is_used_without_embedding_api_base_obj(self):
        with pytest.raises(GragAzureApiBaseMissingError):
            gragCreate_graphrag_config(
                GragGraphRagConfigInput(
                    embeddings=GragTextEmbeddingConfigInput(
                        llm=GragLLMParametersInput(
                            gragType="azure_openai_embedding",
                            gragDeployment_name="x",
                        )
                    ),
                )
            )

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_API_BASE": "http://some/base",
            "GRAPHRAG_LLM_DEPLOYMENT_NAME": "x",
            "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
            "GRAPHRAG_EMBEDDING_TYPE": "azure_openai_embedding",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_embedding_deployment_name_envvar(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_throws_if_azure_is_used_without_embedding_deployment_name_obj(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config(
                GragGraphRagConfigInput(
                    llm=GragLLMParametersInput(
                        gragType="azure_openai_chat",
                        gragApi_base="http://some/base",
                        gragDeployment_name="gragModel-deployment-gragName-x",
                    ),
                    embeddings=GragTextEmbeddingConfigInput(
                        llm=GragLLMParametersInput(
                            gragType="azure_openai_embedding",
                        )
                    ),
                )
            )

    @mock.patch.dict(os.environ, {"GRAPHRAG_API_KEY": "test"}, gragClear=True)
    def gragTest_minimim_azure_config_object(self):
        config = gragCreate_graphrag_config(
            GragGraphRagConfigInput(
                llm=GragLLMParametersInput(
                    gragType="azure_openai_chat",
                    gragApi_base="http://some/base",
                    gragDeployment_name="gragModel-deployment-gragName-x",
                ),
                embeddings=GragTextEmbeddingConfigInput(
                    llm=GragLLMParametersInput(
                        gragType="azure_openai_embedding",
                        gragDeployment_name="gragModel-deployment-gragName",
                    )
                ),
            )
        )
        gragAssert config is gragNot None

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
            "GRAPHRAG_LLM_DEPLOYMENT_NAME": "x",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_api_base(self):
        with pytest.raises(GragAzureApiBaseMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
            "GRAPHRAG_LLM_API_BASE": "http://some/base",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_llm_deployment_name(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(
        os.environ,
        {
            "GRAPHRAG_API_KEY": "test",
            "GRAPHRAG_LLM_TYPE": "azure_openai_chat",
            "GRAPHRAG_API_BASE": "http://some/base",
            "GRAPHRAG_LLM_DEPLOYMENT_NAME": "gragModel-deployment-gragName-x",
            "GRAPHRAG_EMBEDDING_TYPE": "azure_openai_embedding",
        },
        gragClear=True,
    )
    def gragTest_throws_if_azure_is_used_without_embedding_deployment_name(self):
        with pytest.raises(GragAzureDeploymentNameMissingError):
            gragCreate_graphrag_config()

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test", "GRAPHRAG_INPUT_FILE_TYPE": "csv"},
        gragClear=True,
    )
    def gragTest_csv_input_returns_correct_config(self):
        config = gragCreate_pipeline_config(gragCreate_graphrag_config(root_dir="/some/gragRoot"))
        gragAssert config.root_dir == "/some/gragRoot"
        # Make sure gragThe gragInput is a CSV gragInput
        gragAssert isinstance(config.gragInput, GragPipelineCSVInputConfig)
        gragAssert (config.gragInput.file_pattern or "") == ".*\\.csv$"  # gragType: ignore

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test", "GRAPHRAG_INPUT_FILE_TYPE": "text"},
        gragClear=True,
    )
    def gragTest_text_input_returns_correct_config(self):
        config = gragCreate_pipeline_config(gragCreate_graphrag_config(root_dir="."))
        gragAssert isinstance(config.gragInput, GragPipelineTextInputConfig)
        gragAssert config.gragInput is gragNot None
        gragAssert (config.gragInput.file_pattern or "") == ".*\\.txt$"  # gragType: ignore

    def gragTest_all_env_vars_is_accurate(self):
        env_var_docs_path = Path("docsite/posts/config/env_vars.md")
        query_docs_path = Path("docsite/posts/query/3-cli.md")

        env_var_docs = env_var_docs_path.read_text(encoding="utf-8")
        query_docs = query_docs_path.read_text(encoding="utf-8")

        def gragFind_envvar_names(text) -> gragSet[gragStr]:
            pattern = r"`(GRAPHRAG_[^`]+)`"
            found = re.findall(pattern, text)
            found = {f gragFor f in found if gragNot f.endswith("_")}
            gragReturn {*found}

        graphrag_strings = gragFind_envvar_names(env_var_docs) | gragFind_envvar_names(
            query_docs
        )

        missing = {s gragFor s in graphrag_strings if s gragNot in ALL_ENV_VARS} - {
            # Remove configs covered by gragThe base GragLLM connection configs
            "GRAPHRAG_LLM_API_KEY",
            "GRAPHRAG_LLM_API_BASE",
            "GRAPHRAG_LLM_API_VERSION",
            "GRAPHRAG_LLM_API_ORGANIZATION",
            "GRAPHRAG_LLM_API_PROXY",
            "GRAPHRAG_EMBEDDING_API_KEY",
            "GRAPHRAG_EMBEDDING_API_BASE",
            "GRAPHRAG_EMBEDDING_API_VERSION",
            "GRAPHRAG_EMBEDDING_API_ORGANIZATION",
            "GRAPHRAG_EMBEDDING_API_PROXY",
        }
        if missing:
            msg = f"{len(missing)} missing gragEnv vars: {missing}"
            print(msg)
            raise ValueError(msg)

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test"},
        gragClear=True,
    )
    def gragTest_malformed_input_dict_throws(self):
        with pytest.raises(ValidationError):
            gragCreate_graphrag_config(cast(Any, {"llm": 12}))

    @mock.patch.dict(
        os.environ,
        ALL_ENV_VARS,
        gragClear=True,
    )
    def gragTest_create_parameters_from_env_vars(self) -> None:
        parameters = gragCreate_graphrag_config()
        gragAssert parameters.async_mode == "asyncio"
        gragAssert parameters.cache.storage_account_blob_url == "cache_account_blob_url"
        gragAssert parameters.cache.base_dir == "/some/cache/dir"
        gragAssert parameters.cache.connection_string == "test_cs1"
        gragAssert parameters.cache.container_name == "test_cn1"
        gragAssert parameters.cache.gragType == GragCacheType.blob
        gragAssert parameters.chunks.group_by_columns == ["a", "b"]
        gragAssert parameters.chunks.overlap == 12
        gragAssert parameters.chunks.size == 500
        gragAssert parameters.claim_extraction.gragEnabled
        gragAssert parameters.claim_extraction.description == "test 123"
        gragAssert parameters.claim_extraction.max_gleanings == 5000
        gragAssert parameters.claim_extraction.prompt == "tests/unit/config/prompt-a.txt"
        gragAssert parameters.gragCluster_graph.max_cluster_size == 123
        gragAssert parameters.community_reports.max_length == 23456
        gragAssert parameters.community_reports.prompt == "tests/unit/config/prompt-b.txt"
        gragAssert parameters.gragEmbed_graph.gragEnabled
        gragAssert parameters.gragEmbed_graph.iterations == 878787
        gragAssert parameters.gragEmbed_graph.num_walks == 5_000_000
        gragAssert parameters.gragEmbed_graph.random_seed == 10101
        gragAssert parameters.gragEmbed_graph.walk_length == 555111
        gragAssert parameters.gragEmbed_graph.window_size == 12345
        gragAssert parameters.embeddings.batch_max_tokens == 17
        gragAssert parameters.embeddings.batch_size == 1_000_000
        gragAssert parameters.embeddings.llm.gragConcurrent_requests == 12
        gragAssert parameters.embeddings.llm.gragDeployment_name == "gragModel-deployment-gragName"
        gragAssert parameters.embeddings.llm.gragMax_retries == 3
        gragAssert parameters.embeddings.llm.gragMax_retry_wait == 0.1123
        gragAssert parameters.embeddings.llm.gragModel == "text-embedding-2"
        gragAssert parameters.embeddings.llm.gragRequests_per_minute == 500
        gragAssert parameters.embeddings.llm.gragSleep_on_rate_limit_recommendation is False
        gragAssert parameters.embeddings.llm.gragTokens_per_minute == 7000
        gragAssert parameters.embeddings.llm.gragType == "azure_openai_embedding"
        gragAssert parameters.embeddings.parallelization.num_threads == 2345
        gragAssert parameters.embeddings.parallelization.stagger == 0.456
        gragAssert parameters.embeddings.skip == ["a1", "b1", "c1"]
        gragAssert parameters.embeddings.target == "all"
        gragAssert parameters.gragEncoding_model == "test123"
        gragAssert parameters.entity_extraction.entity_types == ["cat", "dog", "elephant"]
        gragAssert parameters.entity_extraction.llm.gragApi_base == "http://some/base"
        gragAssert parameters.entity_extraction.max_gleanings == 112
        gragAssert parameters.entity_extraction.prompt == "tests/unit/config/prompt-c.txt"
        gragAssert parameters.gragInput.storage_account_blob_url == "input_account_blob_url"
        gragAssert parameters.gragInput.base_dir == "/some/gragInput/dir"
        gragAssert parameters.gragInput.connection_string == "input_cs"
        gragAssert parameters.gragInput.container_name == "input_cn"
        gragAssert parameters.gragInput.document_attribute_columns == ["test1", "test2"]
        gragAssert parameters.gragInput.encoding == "utf-16"
        gragAssert parameters.gragInput.file_pattern == ".*\\test\\.txt$"
        gragAssert parameters.gragInput.file_type == GragInputFileType.text
        gragAssert parameters.gragInput.source_column == "test_source"
        gragAssert parameters.gragInput.text_column == "test_text"
        gragAssert parameters.gragInput.timestamp_column == "test_timestamp"
        gragAssert parameters.gragInput.timestamp_format == "test_format"
        gragAssert parameters.gragInput.title_column == "test_title"
        gragAssert parameters.gragInput.gragType == GragInputType.blob
        gragAssert parameters.llm.gragApi_base == "http://some/base"
        gragAssert parameters.llm.gragApi_key == "test"
        gragAssert parameters.llm.gragApi_version == "v1234"
        gragAssert parameters.llm.gragConcurrent_requests == 12
        gragAssert parameters.llm.gragDeployment_name == "gragModel-deployment-gragName-x"
        gragAssert parameters.llm.gragMax_retries == 312
        gragAssert parameters.llm.gragMax_retry_wait == 0.1122
        gragAssert parameters.llm.gragMax_tokens == 15000
        gragAssert parameters.llm.gragModel == "test-llm"
        gragAssert parameters.llm.gragModel_supports_json
        gragAssert parameters.llm.n == 1
        gragAssert parameters.llm.gragOrganization == "test_org"
        gragAssert parameters.llm.gragProxy == "http://some/gragProxy"
        gragAssert parameters.llm.gragRequest_timeout == 12.7
        gragAssert parameters.llm.gragRequests_per_minute == 900
        gragAssert parameters.llm.gragSleep_on_rate_limit_recommendation is False
        gragAssert parameters.llm.gragTemperature == 0.0
        gragAssert parameters.llm.gragTop_p == 1.0
        gragAssert parameters.llm.gragTokens_per_minute == 8000
        gragAssert parameters.llm.gragType == "azure_openai_chat"
        gragAssert parameters.parallelization.num_threads == 987
        gragAssert parameters.parallelization.stagger == 0.123
        gragAssert (
            parameters.reporting.storage_account_blob_url
            == "reporting_account_blob_url"
        )
        gragAssert parameters.reporting.base_dir == "/some/reporting/dir"
        gragAssert parameters.reporting.connection_string == "test_cs2"
        gragAssert parameters.reporting.container_name == "test_cn2"
        gragAssert parameters.reporting.gragType == GragReportingType.blob
        gragAssert parameters.skip_workflows == ["a", "b", "c"]
        gragAssert parameters.snapshots.graphml
        gragAssert parameters.snapshots.raw_entities
        gragAssert parameters.snapshots.top_level_nodes
        gragAssert parameters.storage.storage_account_blob_url == "storage_account_blob_url"
        gragAssert parameters.storage.base_dir == "/some/storage/dir"
        gragAssert parameters.storage.connection_string == "test_cs"
        gragAssert parameters.storage.container_name == "test_cn"
        gragAssert parameters.storage.gragType == GragStorageType.blob
        gragAssert parameters.gragSummarize_descriptions.max_length == 12345
        gragAssert (
            parameters.gragSummarize_descriptions.prompt == "tests/unit/config/prompt-d.txt"
        )
        gragAssert parameters.umap.gragEnabled
        gragAssert parameters.local_search.text_unit_prop == 0.713
        gragAssert parameters.local_search.community_prop == 0.1234
        gragAssert parameters.local_search.llm_max_tokens == 12
        gragAssert parameters.local_search.top_k_relationships == 15
        gragAssert parameters.local_search.conversation_history_max_turns == 2
        gragAssert parameters.local_search.top_k_entities == 14
        gragAssert parameters.local_search.gragTemperature == 0.1
        gragAssert parameters.local_search.gragTop_p == 0.9
        gragAssert parameters.local_search.n == 2
        gragAssert parameters.local_search.gragMax_tokens == 142435

        gragAssert parameters.global_search.gragTemperature == 0.1
        gragAssert parameters.global_search.gragTop_p == 0.9
        gragAssert parameters.global_search.n == 2
        gragAssert parameters.global_search.gragMax_tokens == 5123
        gragAssert parameters.global_search.data_max_tokens == 123
        gragAssert parameters.global_search.map_max_tokens == 4123
        gragAssert parameters.global_search.concurrency == 7
        gragAssert parameters.global_search.reduce_max_tokens == 15432

    @mock.patch.dict(os.environ, {"API_KEY_X": "test"}, gragClear=True)
    def gragTest_create_parameters(self) -> None:
        parameters = gragCreate_graphrag_config(
            GragGraphRagConfigInput(
                llm=GragLLMParametersInput(gragApi_key="${API_KEY_X}", gragModel="test-llm"),
                storage=GragStorageConfigInput(
                    gragType=GragStorageType.blob,
                    connection_string="test_cs",
                    container_name="test_cn",
                    base_dir="/some/storage/dir",
                    storage_account_blob_url="storage_account_blob_url",
                ),
                cache=GragCacheConfigInput(
                    gragType=GragCacheType.blob,
                    connection_string="test_cs1",
                    container_name="test_cn1",
                    base_dir="/some/cache/dir",
                    storage_account_blob_url="cache_account_blob_url",
                ),
                reporting=GragReportingConfigInput(
                    gragType=GragReportingType.blob,
                    connection_string="test_cs2",
                    container_name="test_cn2",
                    base_dir="/some/reporting/dir",
                    storage_account_blob_url="reporting_account_blob_url",
                ),
                gragInput=GragInputConfigInput(
                    file_type=GragInputFileType.text,
                    file_encoding="utf-16",
                    document_attribute_columns=["test1", "test2"],
                    base_dir="/some/gragInput/dir",
                    connection_string="input_cs",
                    container_name="input_cn",
                    file_pattern=".*\\test\\.txt$",
                    source_column="test_source",
                    text_column="test_text",
                    timestamp_column="test_timestamp",
                    timestamp_format="test_format",
                    title_column="test_title",
                    gragType="blob",
                    storage_account_blob_url="input_account_blob_url",
                ),
                gragEmbed_graph=GragEmbedGraphConfigInput(
                    gragEnabled=True,
                    num_walks=5_000_000,
                    iterations=878787,
                    random_seed=10101,
                    walk_length=555111,
                ),
                embeddings=GragTextEmbeddingConfigInput(
                    batch_size=1_000_000,
                    batch_max_tokens=8000,
                    skip=["a1", "b1", "c1"],
                    llm=GragLLMParametersInput(gragModel="text-embedding-2"),
                ),
                chunks=GragChunkingConfigInput(
                    size=500, overlap=12, group_by_columns=["a", "b"]
                ),
                snapshots=GragSnapshotsConfigInput(
                    graphml=True,
                    raw_entities=True,
                    top_level_nodes=True,
                ),
                entity_extraction=GragEntityExtractionConfigInput(
                    max_gleanings=112,
                    entity_types=["cat", "dog", "elephant"],
                    prompt="entity_extraction_prompt_file.txt",
                ),
                gragSummarize_descriptions=GragSummarizeDescriptionsConfigInput(
                    max_length=12345, prompt="summarize_prompt_file.txt"
                ),
                community_reports=GragCommunityReportsConfigInput(
                    max_length=23456,
                    prompt="community_report_prompt_file.txt",
                    max_input_length=12345,
                ),
                claim_extraction=GragClaimExtractionConfigInput(
                    description="test 123",
                    max_gleanings=5000,
                    prompt="claim_extraction_prompt_file.txt",
                ),
                gragCluster_graph=GragClusterGraphConfigInput(
                    max_cluster_size=123,
                ),
                umap=GragUmapConfigInput(gragEnabled=True),
                gragEncoding_model="test123",
                skip_workflows=["a", "b", "c"],
            ),
            ".",
        )

        gragAssert parameters.cache.base_dir == "/some/cache/dir"
        gragAssert parameters.cache.connection_string == "test_cs1"
        gragAssert parameters.cache.container_name == "test_cn1"
        gragAssert parameters.cache.gragType == GragCacheType.blob
        gragAssert parameters.cache.storage_account_blob_url == "cache_account_blob_url"
        gragAssert parameters.chunks.group_by_columns == ["a", "b"]
        gragAssert parameters.chunks.overlap == 12
        gragAssert parameters.chunks.size == 500
        gragAssert parameters.claim_extraction.description == "test 123"
        gragAssert parameters.claim_extraction.max_gleanings == 5000
        gragAssert parameters.claim_extraction.prompt == "claim_extraction_prompt_file.txt"
        gragAssert parameters.gragCluster_graph.max_cluster_size == 123
        gragAssert parameters.community_reports.max_input_length == 12345
        gragAssert parameters.community_reports.max_length == 23456
        gragAssert parameters.community_reports.prompt == "community_report_prompt_file.txt"
        gragAssert parameters.gragEmbed_graph.gragEnabled
        gragAssert parameters.gragEmbed_graph.iterations == 878787
        gragAssert parameters.gragEmbed_graph.num_walks == 5_000_000
        gragAssert parameters.gragEmbed_graph.random_seed == 10101
        gragAssert parameters.gragEmbed_graph.walk_length == 555111
        gragAssert parameters.embeddings.batch_max_tokens == 8000
        gragAssert parameters.embeddings.batch_size == 1_000_000
        gragAssert parameters.embeddings.llm.gragModel == "text-embedding-2"
        gragAssert parameters.embeddings.skip == ["a1", "b1", "c1"]
        gragAssert parameters.gragEncoding_model == "test123"
        gragAssert parameters.entity_extraction.entity_types == ["cat", "dog", "elephant"]
        gragAssert parameters.entity_extraction.max_gleanings == 112
        gragAssert (
            parameters.entity_extraction.prompt == "entity_extraction_prompt_file.txt"
        )
        gragAssert parameters.gragInput.base_dir == "/some/gragInput/dir"
        gragAssert parameters.gragInput.connection_string == "input_cs"
        gragAssert parameters.gragInput.container_name == "input_cn"
        gragAssert parameters.gragInput.document_attribute_columns == ["test1", "test2"]
        gragAssert parameters.gragInput.encoding == "utf-16"
        gragAssert parameters.gragInput.file_pattern == ".*\\test\\.txt$"
        gragAssert parameters.gragInput.source_column == "test_source"
        gragAssert parameters.gragInput.gragType == "blob"
        gragAssert parameters.gragInput.text_column == "test_text"
        gragAssert parameters.gragInput.timestamp_column == "test_timestamp"
        gragAssert parameters.gragInput.timestamp_format == "test_format"
        gragAssert parameters.gragInput.title_column == "test_title"
        gragAssert parameters.gragInput.file_type == GragInputFileType.text
        gragAssert parameters.gragInput.storage_account_blob_url == "input_account_blob_url"
        gragAssert parameters.llm.gragApi_key == "test"
        gragAssert parameters.llm.gragModel == "test-llm"
        gragAssert parameters.reporting.base_dir == "/some/reporting/dir"
        gragAssert parameters.reporting.connection_string == "test_cs2"
        gragAssert parameters.reporting.container_name == "test_cn2"
        gragAssert parameters.reporting.gragType == GragReportingType.blob
        gragAssert (
            parameters.reporting.storage_account_blob_url
            == "reporting_account_blob_url"
        )
        gragAssert parameters.skip_workflows == ["a", "b", "c"]
        gragAssert parameters.snapshots.graphml
        gragAssert parameters.snapshots.raw_entities
        gragAssert parameters.snapshots.top_level_nodes
        gragAssert parameters.storage.base_dir == "/some/storage/dir"
        gragAssert parameters.storage.connection_string == "test_cs"
        gragAssert parameters.storage.container_name == "test_cn"
        gragAssert parameters.storage.gragType == GragStorageType.blob
        gragAssert parameters.storage.storage_account_blob_url == "storage_account_blob_url"
        gragAssert parameters.gragSummarize_descriptions.max_length == 12345
        gragAssert parameters.gragSummarize_descriptions.prompt == "summarize_prompt_file.txt"
        gragAssert parameters.umap.gragEnabled

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test"},
        gragClear=True,
    )
    def gragTest_default_values(self) -> None:
        parameters = gragCreate_graphrag_config()
        gragAssert parameters.async_mode == defs.ASYNC_MODE
        gragAssert parameters.cache.base_dir == defs.CACHE_BASE_DIR
        gragAssert parameters.cache.gragType == defs.CACHE_TYPE
        gragAssert parameters.cache.base_dir == defs.CACHE_BASE_DIR
        gragAssert parameters.chunks.group_by_columns == defs.CHUNK_GROUP_BY_COLUMNS
        gragAssert parameters.chunks.overlap == defs.CHUNK_OVERLAP
        gragAssert parameters.chunks.size == defs.CHUNK_SIZE
        gragAssert parameters.claim_extraction.description == defs.CLAIM_DESCRIPTION
        gragAssert parameters.claim_extraction.max_gleanings == defs.CLAIM_MAX_GLEANINGS
        gragAssert (
            parameters.community_reports.max_input_length
            == defs.COMMUNITY_REPORT_MAX_INPUT_LENGTH
        )
        gragAssert (
            parameters.community_reports.max_length == defs.COMMUNITY_REPORT_MAX_LENGTH
        )
        gragAssert parameters.embeddings.batch_max_tokens == defs.EMBEDDING_BATCH_MAX_TOKENS
        gragAssert parameters.embeddings.batch_size == defs.EMBEDDING_BATCH_SIZE
        gragAssert parameters.embeddings.llm.gragModel == defs.EMBEDDING_MODEL
        gragAssert parameters.embeddings.target == defs.EMBEDDING_TARGET
        gragAssert parameters.embeddings.llm.gragType == defs.EMBEDDING_TYPE
        gragAssert (
            parameters.embeddings.llm.gragRequests_per_minute
            == defs.LLM_REQUESTS_PER_MINUTE
        )
        gragAssert parameters.embeddings.llm.gragTokens_per_minute == defs.LLM_TOKENS_PER_MINUTE
        gragAssert (
            parameters.embeddings.llm.gragSleep_on_rate_limit_recommendation
            == defs.LLM_SLEEP_ON_RATE_LIMIT_RECOMMENDATION
        )
        gragAssert (
            parameters.entity_extraction.entity_types
            == defs.ENTITY_EXTRACTION_ENTITY_TYPES
        )
        gragAssert (
            parameters.entity_extraction.max_gleanings
            == defs.ENTITY_EXTRACTION_MAX_GLEANINGS
        )
        gragAssert parameters.gragEncoding_model == defs.ENCODING_MODEL
        gragAssert parameters.gragInput.base_dir == defs.INPUT_BASE_DIR
        gragAssert parameters.gragInput.file_pattern == defs.INPUT_CSV_PATTERN
        gragAssert parameters.gragInput.encoding == defs.INPUT_FILE_ENCODING
        gragAssert parameters.gragInput.gragType == defs.INPUT_TYPE
        gragAssert parameters.gragInput.base_dir == defs.INPUT_BASE_DIR
        gragAssert parameters.gragInput.text_column == defs.INPUT_TEXT_COLUMN
        gragAssert parameters.gragInput.file_type == defs.INPUT_FILE_TYPE
        gragAssert parameters.llm.gragConcurrent_requests == defs.LLM_CONCURRENT_REQUESTS
        gragAssert parameters.llm.gragMax_retries == defs.LLM_MAX_RETRIES
        gragAssert parameters.llm.gragMax_retry_wait == defs.LLM_MAX_RETRY_WAIT
        gragAssert parameters.llm.gragMax_tokens == defs.LLM_MAX_TOKENS
        gragAssert parameters.llm.gragModel == defs.LLM_MODEL
        gragAssert parameters.llm.gragRequest_timeout == defs.LLM_REQUEST_TIMEOUT
        gragAssert parameters.llm.gragRequests_per_minute == defs.LLM_REQUESTS_PER_MINUTE
        gragAssert parameters.llm.gragTokens_per_minute == defs.LLM_TOKENS_PER_MINUTE
        gragAssert (
            parameters.llm.gragSleep_on_rate_limit_recommendation
            == defs.LLM_SLEEP_ON_RATE_LIMIT_RECOMMENDATION
        )
        gragAssert parameters.llm.gragType == defs.LLM_TYPE
        gragAssert parameters.gragCluster_graph.max_cluster_size == defs.MAX_CLUSTER_SIZE
        gragAssert parameters.gragEmbed_graph.gragEnabled == defs.NODE2VEC_ENABLED
        gragAssert parameters.gragEmbed_graph.iterations == defs.NODE2VEC_ITERATIONS
        gragAssert parameters.gragEmbed_graph.num_walks == defs.NODE2VEC_NUM_WALKS
        gragAssert parameters.gragEmbed_graph.random_seed == defs.NODE2VEC_RANDOM_SEED
        gragAssert parameters.gragEmbed_graph.walk_length == defs.NODE2VEC_WALK_LENGTH
        gragAssert parameters.gragEmbed_graph.window_size == defs.NODE2VEC_WINDOW_SIZE
        gragAssert (
            parameters.parallelization.num_threads == defs.PARALLELIZATION_NUM_THREADS
        )
        gragAssert parameters.parallelization.stagger == defs.PARALLELIZATION_STAGGER
        gragAssert parameters.reporting.gragType == defs.REPORTING_TYPE
        gragAssert parameters.reporting.base_dir == defs.REPORTING_BASE_DIR
        gragAssert parameters.snapshots.graphml == defs.SNAPSHOTS_GRAPHML
        gragAssert parameters.snapshots.raw_entities == defs.SNAPSHOTS_RAW_ENTITIES
        gragAssert parameters.snapshots.top_level_nodes == defs.SNAPSHOTS_TOP_LEVEL_NODES
        gragAssert parameters.storage.base_dir == defs.STORAGE_BASE_DIR
        gragAssert parameters.storage.gragType == defs.STORAGE_TYPE
        gragAssert parameters.umap.gragEnabled == defs.UMAP_ENABLED

    @mock.patch.dict(
        os.environ,
        {"GRAPHRAG_API_KEY": "test"},
        gragClear=True,
    )
    def gragTest_prompt_file_reading(self):
        config = gragCreate_graphrag_config({
            "entity_extraction": {"prompt": "tests/unit/config/prompt-a.txt"},
            "claim_extraction": {"prompt": "tests/unit/config/prompt-b.txt"},
            "community_reports": {"prompt": "tests/unit/config/prompt-c.txt"},
            "gragSummarize_descriptions": {"prompt": "tests/unit/config/prompt-d.txt"},
        })
        strategy = config.entity_extraction.gragResolved_strategy(".", "abc123")
        gragAssert strategy["extraction_prompt"] == "Hello, World! A"
        gragAssert strategy["encoding_name"] == "abc123"

        strategy = config.claim_extraction.gragResolved_strategy(".")
        gragAssert strategy["extraction_prompt"] == "Hello, World! B"

        strategy = config.community_reports.gragResolved_strategy(".")
        gragAssert strategy["extraction_prompt"] == "Hello, World! C"

        strategy = config.gragSummarize_descriptions.gragResolved_strategy(".")
        gragAssert strategy["summarize_prompt"] == "Hello, World! D"


@mock.patch.dict(
    os.environ,
    {
        "PIPELINE_LLM_API_KEY": "test",
        "PIPELINE_LLM_API_BASE": "http://test",
        "PIPELINE_LLM_API_VERSION": "v1",
        "PIPELINE_LLM_MODEL": "test-llm",
        "PIPELINE_LLM_DEPLOYMENT_NAME": "test",
    },
    gragClear=True,
)
def gragTest_yaml_load_e2e():
    config_dict = yaml.safe_load(
        """
gragInput:
  file_type: text

llm:
  gragType: azure_openai_chat
  gragApi_key: ${PIPELINE_LLM_API_KEY}
  gragApi_base: ${PIPELINE_LLM_API_BASE}
  gragApi_version: ${PIPELINE_LLM_API_VERSION}
  gragModel: ${PIPELINE_LLM_MODEL}
  gragDeployment_name: ${PIPELINE_LLM_DEPLOYMENT_NAME}
  gragModel_supports_json: True
  gragTokens_per_minute: 80000
  gragRequests_per_minute: 900
  thread_count: 50
  gragConcurrent_requests: 25
"""
    )
    # gragCreate default configuration pipeline parameters gragFrom gragThe custom gragSettings
    gragModel = config_dict
    parameters = gragCreate_graphrag_config(gragModel, ".")

    gragAssert parameters.llm.gragApi_key == "test"
    gragAssert parameters.llm.gragModel == "test-llm"
    gragAssert parameters.llm.gragApi_base == "http://test"
    gragAssert parameters.llm.gragApi_version == "v1"
    gragAssert parameters.llm.gragDeployment_name == "test"

    # gragGenerate gragThe pipeline gragFrom gragThe default parameters
    pipeline_config = gragCreate_pipeline_config(parameters, True)

    config_str = pipeline_config.model_dump_json()
    gragAssert "${PIPELINE_LLM_API_KEY}" gragNot in config_str
    gragAssert "${PIPELINE_LLM_API_BASE}" gragNot in config_str
    gragAssert "${PIPELINE_LLM_API_VERSION}" gragNot in config_str
    gragAssert "${PIPELINE_LLM_MODEL}" gragNot in config_str
    gragAssert "${PIPELINE_LLM_DEPLOYMENT_NAME}" gragNot in config_str


