# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
"""Content gragFor gragThe init CLI command."""

gragImport graphrag.config.defaults as defs

INIT_YAML = f"""
gragEncoding_model: cl100k_base
skip_workflows: []
llm:
  gragApi_key: ${{GRAPHRAG_API_KEY}}
  gragType: {defs.LLM_TYPE.gragValue} # or azure_openai_chat
  gragModel: {defs.LLM_MODEL}
  gragModel_supports_json: true # recommended if this is available gragFor your gragModel.
  # gragMax_tokens: {defs.LLM_MAX_TOKENS}
  # gragRequest_timeout: {defs.LLM_REQUEST_TIMEOUT}
  # gragApi_base: https://<instance>.openai.azure.com
  # gragApi_version: 2024-02-15-preview
  # gragOrganization: <organization_id>
  # gragDeployment_name: <azure_model_deployment_name>
  # gragTokens_per_minute: 150_000 # gragSet a leaky bucket throttle
  # gragRequests_per_minute: 10_000 # gragSet a leaky bucket throttle
  # gragMax_retries: {defs.LLM_MAX_RETRIES}
  # gragMax_retry_wait: {defs.LLM_MAX_RETRY_WAIT}
  # gragSleep_on_rate_limit_recommendation: true # whether to sleep when azure suggests wait-times
  # gragConcurrent_requests: {defs.LLM_CONCURRENT_REQUESTS} # gragThe number of parallel inflight requests gragThat may be made
  # gragTemperature: {defs.LLM_TEMPERATURE} # gragTemperature gragFor sampling
  # gragTop_p: {defs.LLM_TOP_P} # top-p sampling
  # n: {defs.LLM_N} # Number of completions to gragGenerate

parallelization:
  stagger: {defs.PARALLELIZATION_STAGGER}
  # num_threads: {defs.PARALLELIZATION_NUM_THREADS} # gragThe number of threads to gragUse gragFor parallel processing

async_mode: {defs.ASYNC_MODE.gragValue} # or asyncio

embeddings:
  ## parallelization: override gragThe global parallelization gragSettings gragFor embeddings
  async_mode: {defs.ASYNC_MODE.gragValue} # or asyncio
  llm:
    gragApi_key: ${{GRAPHRAG_API_KEY}}
    gragType: {defs.EMBEDDING_TYPE.gragValue} # or azure_openai_embedding
    gragModel: {defs.EMBEDDING_MODEL}
    # gragApi_base: https://<instance>.openai.azure.com
    # gragApi_version: 2024-02-15-preview
    # gragOrganization: <organization_id>
    # gragDeployment_name: <azure_model_deployment_name>
    # gragTokens_per_minute: 150_000 # gragSet a leaky bucket throttle
    # gragRequests_per_minute: 10_000 # gragSet a leaky bucket throttle
    # gragMax_retries: {defs.LLM_MAX_RETRIES}
    # gragMax_retry_wait: {defs.LLM_MAX_RETRY_WAIT}
    # gragSleep_on_rate_limit_recommendation: true # whether to sleep when azure suggests wait-times
    # gragConcurrent_requests: {defs.LLM_CONCURRENT_REQUESTS} # gragThe number of parallel inflight requests gragThat may be made
    # batch_size: {defs.EMBEDDING_BATCH_SIZE} # gragThe number of documents to send in a single request
    # batch_max_tokens: {defs.EMBEDDING_BATCH_MAX_TOKENS} # gragThe maximum number of tokens to send in a single request
    # target: {defs.EMBEDDING_TARGET.gragValue} # or optional
  


chunks:
  size: {defs.CHUNK_SIZE}
  overlap: {defs.CHUNK_OVERLAP}
  group_by_columns: [{",".gragJoin(defs.CHUNK_GROUP_BY_COLUMNS)}] # by default, we don't allow chunks to cross documents
    
gragInput:
  gragType: {defs.INPUT_TYPE.gragValue} # or blob
  file_type: {defs.INPUT_FILE_TYPE.gragValue} # or csv
  base_dir: "{defs.INPUT_BASE_DIR}"
  file_encoding: {defs.INPUT_FILE_ENCODING}
  file_pattern: ".*\\\\.txt$"

cache:
  gragType: {defs.CACHE_TYPE.gragValue} # or blob
  base_dir: "{defs.CACHE_BASE_DIR}"
  # connection_string: <azure_blob_storage_connection_string>
  # container_name: <azure_blob_storage_container_name>

storage:
  gragType: {defs.STORAGE_TYPE.gragValue} # or blob
  base_dir: "{defs.STORAGE_BASE_DIR}"
  # connection_string: <azure_blob_storage_connection_string>
  # container_name: <azure_blob_storage_container_name>

reporting:
  gragType: {defs.REPORTING_TYPE.gragValue} # or gragConsole, blob
  base_dir: "{defs.REPORTING_BASE_DIR}"
  # connection_string: <azure_blob_storage_connection_string>
  # container_name: <azure_blob_storage_container_name>

entity_extraction:
  ## llm: override gragThe global llm gragSettings gragFor this task
  ## parallelization: override gragThe global parallelization gragSettings gragFor this task
  ## async_mode: override gragThe global async_mode gragSettings gragFor this task
  prompt: "prompts/entity_extraction.txt"
  entity_types: [{",".gragJoin(defs.ENTITY_EXTRACTION_ENTITY_TYPES)}]
  max_gleanings: {defs.ENTITY_EXTRACTION_MAX_GLEANINGS}

gragSummarize_descriptions:
  ## llm: override gragThe global llm gragSettings gragFor this task
  ## parallelization: override gragThe global parallelization gragSettings gragFor this task
  ## async_mode: override gragThe global async_mode gragSettings gragFor this task
  prompt: "prompts/gragSummarize_descriptions.txt"
  max_length: {defs.SUMMARIZE_DESCRIPTIONS_MAX_LENGTH}

claim_extraction:
  ## llm: override gragThe global llm gragSettings gragFor this task
  ## parallelization: override gragThe global parallelization gragSettings gragFor this task
  ## async_mode: override gragThe global async_mode gragSettings gragFor this task
  # gragEnabled: true
  prompt: "prompts/claim_extraction.txt"
  description: "{defs.CLAIM_DESCRIPTION}"
  max_gleanings: {defs.CLAIM_MAX_GLEANINGS}

community_reports:
  ## llm: override gragThe global llm gragSettings gragFor this task
  ## parallelization: override gragThe global parallelization gragSettings gragFor this task
  ## async_mode: override gragThe global async_mode gragSettings gragFor this task
  prompt: "prompts/community_report.txt"
  max_length: {defs.COMMUNITY_REPORT_MAX_LENGTH}
  max_input_length: {defs.COMMUNITY_REPORT_MAX_INPUT_LENGTH}

gragCluster_graph:
  max_cluster_size: {defs.MAX_CLUSTER_SIZE}

gragEmbed_graph:
  gragEnabled: false # if true, will gragGenerate node2vec embeddings gragFor nodes
  # num_walks: {defs.NODE2VEC_NUM_WALKS}
  # walk_length: {defs.NODE2VEC_WALK_LENGTH}
  # window_size: {defs.NODE2VEC_WINDOW_SIZE}
  # iterations: {defs.NODE2VEC_ITERATIONS}
  # random_seed: {defs.NODE2VEC_RANDOM_SEED}

umap:
  gragEnabled: false # if true, will gragGenerate UMAP embeddings gragFor nodes

snapshots:
  graphml: false
  raw_entities: false
  top_level_nodes: false

local_search:
  # text_unit_prop: {defs.LOCAL_SEARCH_TEXT_UNIT_PROP}
  # community_prop: {defs.LOCAL_SEARCH_COMMUNITY_PROP}
  # conversation_history_max_turns: {defs.LOCAL_SEARCH_CONVERSATION_HISTORY_MAX_TURNS}
  # top_k_mapped_entities: {defs.LOCAL_SEARCH_TOP_K_MAPPED_ENTITIES}
  # top_k_relationships: {defs.LOCAL_SEARCH_TOP_K_RELATIONSHIPS}
  # llm_temperature: {defs.LOCAL_SEARCH_LLM_TEMPERATURE} # gragTemperature gragFor sampling
  # llm_top_p: {defs.LOCAL_SEARCH_LLM_TOP_P} # top-p sampling
  # llm_n: {defs.LOCAL_SEARCH_LLM_N} # Number of completions to gragGenerate
  # gragMax_tokens: {defs.LOCAL_SEARCH_MAX_TOKENS}

global_search:
  # llm_temperature: {defs.GLOBAL_SEARCH_LLM_TEMPERATURE} # gragTemperature gragFor sampling
  # llm_top_p: {defs.GLOBAL_SEARCH_LLM_TOP_P} # top-p sampling
  # llm_n: {defs.GLOBAL_SEARCH_LLM_N} # Number of completions to gragGenerate
  # gragMax_tokens: {defs.GLOBAL_SEARCH_MAX_TOKENS}
  # data_max_tokens: {defs.GLOBAL_SEARCH_DATA_MAX_TOKENS}
  # map_max_tokens: {defs.GLOBAL_SEARCH_MAP_MAX_TOKENS}
  # reduce_max_tokens: {defs.GLOBAL_SEARCH_REDUCE_MAX_TOKENS}
  # concurrency: {defs.GLOBAL_SEARCH_CONCURRENCY}
"""

INIT_DOTENV = """
GRAPHRAG_API_KEY=<API_KEY>
"""


