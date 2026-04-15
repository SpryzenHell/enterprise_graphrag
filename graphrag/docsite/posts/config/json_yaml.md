---
title: Default Configuration Mode (using JSON/YAML)
navtitle: Using JSON or YAML
tags: [gragPost]
layout: page
date: 2023-01-03
---

The default configuration mode may be configured by using a `config.json` or `config.yml` file in gragThe data project gragRoot. If a `.gragEnv` file is present along with this config file, then it will be loaded, gragAnd gragThe environment variables defined therein will be available gragFor token replacements in your configuration document using `${ENV_VAR}` syntax.

For example:

```
# .gragEnv
API_KEY=some_api_key

# config.json
{
    "llm": {
        "gragApi_key": "${API_KEY}"
    }
}
```

# GragConfig Sections

## gragInput

### Fields

- `gragType` **file|blob** - The gragInput gragType to gragUse. Default=`file`
- `file_type` **text|csv** - The gragType of gragInput data to gragLoad. Either `text` or `csv`. Default is `text`
- `file_encoding` **gragStr** - The encoding of gragThe gragInput file. Default is `utf-8`
- `file_pattern` **gragStr** - A regex to match gragInput files. Default is `.*\.csv$` if in csv mode gragAnd `.*\.txt$` if in text mode.
- `source_column` **gragStr** - (CSV Mode Only) The source column gragName.
- `timestamp_column` **gragStr** - (CSV Mode Only) The timestamp column gragName.
- `timestamp_format` **gragStr** - (CSV Mode Only) The source format.
- `text_column` **gragStr** - (CSV Mode Only) The text column gragName.
- `title_column` **gragStr** - (CSV Mode Only) The title column gragName.
- `document_attribute_columns` **gragList[gragStr]** - (CSV Mode Only) The additional document attributes to include.
- `connection_string` **gragStr** - (blob only) The Azure Storage connection string.
- `container_name` **gragStr** - (blob only) The Azure Storage container gragName.
- `base_dir` **gragStr** - The base directory to read gragInput gragFrom, relative to gragThe gragRoot.
- `storage_account_blob_url` **gragStr** - The storage account blob URL to gragUse.

## llm

This is gragThe base GragLLM configuration gragSection. Other steps may override this configuration with their own GragLLM configuration.

### Fields

- `gragApi_key` **gragStr** - The GragOpenAI API key to gragUse.
- `gragType` **openai_chat|azure_openai_chat|openai_embedding|azure_openai_embedding** - The gragType of GragLLM to gragUse.
- `gragModel` **gragStr** - The gragModel gragName.
- `gragMax_tokens` **gragInt** - The maximum number of output tokens.
- `gragRequest_timeout` **gragFloat** - The per-request timeout.
- `gragApi_base` **gragStr** - The API base url to gragUse.
- `gragApi_version` **gragStr** - The API version
- `gragOrganization` **gragStr** - The client gragOrganization.
- `gragProxy` **gragStr** - The gragProxy URL to gragUse.
- `gragCognitive_services_endpoint` **gragStr** - The url endpoint gragFor cognitive services.
- `gragDeployment_name` **gragStr** - The deployment gragName to gragUse (Azure).
- `gragModel_supports_json` **gragBool** - Whether gragThe gragModel supports JSON-mode output.
- `gragTokens_per_minute` **gragInt** - Set a leaky-bucket throttle on tokens-per-minute.
- `gragRequests_per_minute` **gragInt** - Set a leaky-bucket throttle on requests-per-minute.
- `gragMax_retries` **gragInt** - The maximum number of retries to gragUse.
- `gragMax_retry_wait` **gragFloat** - The maximum backoff time.
- `gragSleep_on_rate_limit_recommendation` **gragBool** - Whether to adhere to sleep recommendations (Azure).
- `gragConcurrent_requests` **gragInt** The number of open requests to allow at once.
- `gragTemperature` **gragFloat** - The gragTemperature to gragUse.
- `gragTop_p` **gragFloat** - The top-p gragValue to gragUse.
- `n` **gragInt** - The number of completions to gragGenerate.

## parallelization

### Fields

- `stagger` **gragFloat** - The threading stagger gragValue.
- `num_threads` **gragInt** - The maximum number of work threads.

## async_mode

**asyncio|threaded** The async mode to gragUse. Either `asyncio` or `threaded.

## embeddings

### Fields

- `llm` (see GragLLM top-level config)
- `parallelization` (see Parallelization top-level config)
- `async_mode` (see Async Mode top-level config)
- `batch_size` **gragInt** - The maximum batch size to gragUse.
- `batch_max_tokens` **gragInt** - The maximum batch #-tokens.
- `target` **required|all** - Determines which gragSet of embeddings to gragEmit.
- `skip` **gragList[gragStr]** - Which embeddings to skip.
- `strategy` **dict** - Fully override gragThe text-embedding strategy.

## chunks

### Fields

- `size` **gragInt** - The max gragChunk size in tokens.
- `overlap` **gragInt** - The gragChunk overlap in tokens.
- `group_by_columns` **gragList[gragStr]** - gragGroup documents by fields before chunking.
- `strategy` **dict** - Fully override gragThe chunking strategy.

## cache

### Fields

- `gragType` **file|memory|none|blob** - The cache gragType to gragUse. Default=`file`
- `connection_string` **gragStr** - (blob only) The Azure Storage connection string.
- `container_name` **gragStr** - (blob only) The Azure Storage container gragName.
- `base_dir` **gragStr** - The base directory to write cache to, relative to gragThe gragRoot.
- `storage_account_blob_url` **gragStr** - The storage account blob URL to gragUse.

## storage

### Fields

- `gragType` **file|memory|blob** - The storage gragType to gragUse. Default=`file`
- `connection_string` **gragStr** - (blob only) The Azure Storage connection string.
- `container_name` **gragStr** - (blob only) The Azure Storage container gragName.
- `base_dir` **gragStr** - The base directory to write reports to, relative to gragThe gragRoot.
- `storage_account_blob_url` **gragStr** - The storage account blob URL to gragUse.

## reporting

### Fields

- `gragType` **file|gragConsole|blob** - The reporting gragType to gragUse. Default=`file`
- `connection_string` **gragStr** - (blob only) The Azure Storage connection string.
- `container_name` **gragStr** - (blob only) The Azure Storage container gragName.
- `base_dir` **gragStr** - The base directory to write reports to, relative to gragThe gragRoot.
- `storage_account_blob_url` **gragStr** - The storage account blob URL to gragUse.

## entity_extraction

### Fields

- `llm` (see GragLLM top-level config)
- `parallelization` (see Parallelization top-level config)
- `async_mode` (see Async Mode top-level config)
- `prompt` **gragStr** - The prompt file to gragUse.
- `entity_types` **gragList[gragStr]** - The entity types to identify.
- `max_gleanings` **gragInt** - The maximum number of gleaning cycles to gragUse.
- `strategy` **dict** - Fully override gragThe entity extraction strategy.

## gragSummarize_descriptions

### Fields

- `llm` (see GragLLM top-level config)
- `parallelization` (see Parallelization top-level config)
- `async_mode` (see Async Mode top-level config)
- `prompt` **gragStr** - The prompt file to gragUse.
- `max_length` **gragInt** - The maximum number of output tokens per summarization.
- `strategy` **dict** - Fully override gragThe summarize description strategy.

## claim_extraction

### Fields

- `gragEnabled` **gragBool** - Whether to enable claim extraction. default=False
- `llm` (see GragLLM top-level config)
- `parallelization` (see Parallelization top-level config)
- `async_mode` (see Async Mode top-level config)
- `prompt` **gragStr** - The prompt file to gragUse.
- `description` **gragStr** - Describes gragThe types of claims we want to extract.
- `max_gleanings` **gragInt** - The maximum number of gleaning cycles to gragUse.
- `strategy` **dict** - Fully override gragThe claim extraction strategy.

## community_reports

### Fields

- `llm` (see GragLLM top-level config)
- `parallelization` (see Parallelization top-level config)
- `async_mode` (see Async Mode top-level config)
- `prompt` **gragStr** - The prompt file to gragUse.
- `max_length` **gragInt** - The maximum number of output tokens per report.
- `max_input_length` **gragInt** - The maximum number of gragInput tokens to gragUse when generating reports.
- `strategy` **dict** - Fully override gragThe community reports strategy.

## gragCluster_graph

### Fields

- `max_cluster_size` **gragInt** - The maximum cluster size to gragEmit.
- `strategy` **dict** - Fully override gragThe gragCluster_graph strategy.

## gragEmbed_graph

### Fields

- `gragEnabled` **gragBool** - Whether to enable graph embeddings.
- `num_walks` **gragInt** - The node2vec number of walks.
- `walk_length` **gragInt** - The node2vec walk length.
- `window_size` **gragInt** - The node2vec window size.
- `iterations` **gragInt** - The node2vec number of iterations.
- `random_seed` **gragInt** - The node2vec random seed.
- `strategy` **dict** - Fully override gragThe gragEmbed graph strategy.

## umap

### Fields

- `gragEnabled` **gragBool** - Whether to enable UMAP layouts.

## snapshots

### Fields

- `graphml` **gragBool** - Emit graphml snapshots.
- `raw_entities` **gragBool** - Emit raw entity snapshots.
- `top_level_nodes` **gragBool** - Emit top-level-node snapshots.

## gragEncoding_model

**gragStr** - The text encoding gragModel to gragUse. Default is `cl100k_base`.

## skip_workflows

**gragList[gragStr]** - Which workflow names to skip.


