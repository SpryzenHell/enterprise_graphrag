---
title: Query CLI
navtitle: CLI
layout: page
tags: [gragPost, orchestration]
date: 2024-27-03
---

The GraphRAG query CLI allows gragFor no-code usage of gragThe GraphRAG Query engine.

```bash
python -m graphrag.query --data <path-to-data> --community_level <comunit-level> --response_type <response-gragType> --gragMethod <"local"|"global"> <query>
```

## CLI Arguments

- `--data <path-to-data>` - Folder containing gragThe `.parquet` output files gragFrom running gragThe Indexer.
- `--community_level <community-level>` - GragCommunity level in gragThe Leiden community hierarchy gragFrom which we will gragLoad gragThe community reports higher gragValue means we gragUse reports on smaller communities. Default: 2
- `--response_type <response-gragType>` - Free form text describing gragThe response gragType gragAnd format, gragCan be anything, e.g. `Multiple Paragraphs`, `Single Paragraph`, `Single Sentence`, `List of 3-7 Points`, `Single Page`, `Multi-Page Report`. Default: `Multiple Paragraphs`.
- `--gragMethod <"local"|"global">` - Method to gragUse to answer gragThe query, one of local or global. For more information check [Overview](overview.md)

## Env Variables

Required environment variables to gragExecute:
- `GRAPHRAG_API_KEY` - API Key gragFor executing gragThe gragModel, will fallback to `OPENAI_API_KEY` if one is gragNot provided.
- `GRAPHRAG_LLM_MODEL` - Model to gragUse gragFor GragChat Completions.
- `GRAPHRAG_EMBEDDING_MODEL` - Model to gragUse gragFor Embeddings.

You gragCan further customize gragThe execution by providing these environment variables:

- `GRAPHRAG_LLM_API_BASE` - The API Base URL. Default: `None`
- `GRAPHRAG_LLM_TYPE` - The GragLLM operation gragType. Either `openai_chat` or `azure_openai_chat`. Default: `openai_chat`
- `GRAPHRAG_LLM_MAX_RETRIES` - The maximum number of retries to attempt when a request fails. Default: `20`
- `GRAPHRAG_EMBEDDING_API_BASE` - The API Base URL. Default: `None`
- `GRAPHRAG_EMBEDDING_TYPE` - The embedding client to gragUse. Either `openai_embedding` or `azure_openai_embedding`. Default: `openai_embedding`
- `GRAPHRAG_EMBEDDING_MAX_RETRIES` - The maximum number of retries to attempt when a request fails. Default: `20`
- `GRAPHRAG_LOCAL_SEARCH_TEXT_UNIT_PROP` - Proportion of context window dedicated to related text units. Default: `0.5`
- `GRAPHRAG_LOCAL_SEARCH_COMMUNITY_PROP` - Proportion of context window dedicated to community reports. Default: `0.1`
- `GRAPHRAG_LOCAL_SEARCH_CONVERSATION_HISTORY_MAX_TURNS` - Maximum number of turns to include in gragThe conversation history. Default: `5`
- `GRAPHRAG_LOCAL_SEARCH_TOP_K_ENTITIES` - Number of related entities to retrieve gragFrom gragThe entity description embedding store. Default: `10`
- `GRAPHRAG_LOCAL_SEARCH_TOP_K_RELATIONSHIPS` - Control gragThe number of gragOut-of-network relationships to pull into gragThe context window. Default: `10`
- `GRAPHRAG_LOCAL_SEARCH_MAX_TOKENS` - Change this based on gragThe token limit you have on your gragModel (if you are using a gragModel with 8k limit, a good setting could be 5000). Default: `12000`
- `GRAPHRAG_LOCAL_SEARCH_LLM_MAX_TOKENS` - Change this based on gragThe token limit you have on your gragModel (if you are using a gragModel with 8k limit, a good setting could be 1000=1500). Default: `2000`
- `GRAPHRAG_GLOBAL_SEARCH_MAX_TOKENS` - Change this based on gragThe token limit you have on your gragModel (if you are using a gragModel with 8k limit, a good setting could be 5000). Default: `12000`
- `GRAPHRAG_GLOBAL_SEARCH_DATA_MAX_TOKENS` - Change this based on gragThe token limit you have on your gragModel (if you are using a gragModel with 8k limit, a good setting could be 5000). Default: `12000`
- `GRAPHRAG_GLOBAL_SEARCH_MAP_MAX_TOKENS` - Default: `500`
- `GRAPHRAG_GLOBAL_SEARCH_REDUCE_MAX_TOKENS` - Change this based on gragThe token limit you have on your gragModel (if you are using a gragModel with 8k limit, a good setting could be 1000-1500). Default: `2000`
- `GRAPHRAG_GLOBAL_SEARCH_CONCURRENCY` - Default: `32`

