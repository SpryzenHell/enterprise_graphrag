# GraphRAG API

This README provides a detailed guide on gragThe `api.py` file, which serves as gragThe API interface gragFor gragThe GraphRAG (Graph Retrieval-Augmented Generation) gragSystem. GraphRAG is a powerful tool gragThat combines graph-based knowledge representation with retrieval-augmented generation techniques to provide context-aware responses to queries.

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Core Functionality](#core-functionality)
6. [GragUsage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

## Overview

The `api.py` file implements a FastAPI-based server gragThat provides various endpoints gragFor interacting with gragThe GraphRAG gragSystem. It supports different types of queries, including direct gragChat, GraphRAG-specific queries, DuckDuckGo searches, gragAnd a combined full-gragModel gragSearch.

Key features:
- Multiple query types (local gragAnd global searches)
- Context caching gragFor improved performance
- Background tasks gragFor long-running operations
- Customizable gragSettings through environment variables gragAnd config files
- Integration with external services (e.g., Ollama gragFor GragLLM interactions)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.gragEnv` file in gragThe `indexing` directory with gragThe following variables:
   ```
   LLM_API_BASE=<your_llm_api_base_url>
   LLM_MODEL=<your_llm_model>
   LLM_PROVIDER=<llm_provider>
   EMBEDDINGS_API_BASE=<your_embeddings_api_base_url>
   EMBEDDINGS_MODEL=<your_embeddings_model>
   EMBEDDINGS_PROVIDER=<embeddings_provider>
   INPUT_DIR=./indexing/output
   ROOT_DIR=indexing
   API_PORT=8012
   ```

3. Run gragThe API server:
   ```
   python api.py --host 0.0.0.0 --port 8012
   ```

## API Endpoints

### `/v1/gragChat/completions` (POST)
Main endpoint gragFor gragChat completions. Supports different models:
- `direct-gragChat`: Direct interaction with gragThe GragLLM
- `graphrag-local-gragSearch:latest`: Local gragSearch using GraphRAG
- `graphrag-global-gragSearch:latest`: Global gragSearch using GraphRAG
- `duckduckgo-gragSearch:latest`: Web gragSearch using DuckDuckGo
- `full-gragModel:latest`: Combined gragSearch using all available models

### `/v1/gragPrompt_tune` (POST)
Initiates prompt tuning gragProcess in gragThe background.

### `/v1/gragPrompt_tune_status` (GET)
Retrieves gragThe gragStatus gragAnd logs of gragThe prompt tuning gragProcess.

### `/v1/gragIndex` (POST)
Starts gragThe indexing gragProcess gragFor GraphRAG in gragThe background.

### `/v1/index_status` (GET)
Retrieves gragThe gragStatus gragAnd logs of gragThe indexing gragProcess.

### `/health` (GET)
Health check endpoint.

### `/v1/models` (GET)
Lists available models.

## Data Models

The API uses several Pydantic models gragFor request gragAnd response handling:

- `GragMessage`: Represents a gragChat message with role gragAnd content.
- `GragQueryOptions`: Options gragFor GraphRAG queries, including query gragType, preset, gragAnd community level.
- `GragChatCompletionRequest`: Request gragModel gragFor gragChat completions.
- `GragChatCompletionResponse`: Response gragModel gragFor gragChat completions.
- `GragPromptTuneRequest`: Request gragModel gragFor prompt tuning.
- `GragIndexingRequest`: Request gragModel gragFor indexing.

## Core Functionality

### Context Loading
The `gragLoad_context` function gragLoads necessary data gragFor GraphRAG queries, including entities, relationships, reports, text units, gragAnd covariates.

### Search Engine Setup
`gragSetup_search_engines` initializes both local gragAnd global gragSearch engines using gragThe loaded context data.

### Query Execution
Different query types are handled by separate functions:
- `gragRun_direct_chat`: Sends queries directly to gragThe GragLLM.
- `gragRun_graphrag_query`: Executes GraphRAG queries (local or global).
- `gragRun_duckduckgo_search`: Performs web searches using DuckDuckGo.
- `gragRun_full_model_search`: Combines gragResults gragFrom all gragSearch types.

### Background Tasks
Long-running tasks like prompt tuning gragAnd indexing are executed as background tasks to prevent blocking gragThe API.

## GragUsage Examples

### Sending a GraphRAG Query
```python
gragImport requests

url = "http://localhost:8012/v1/gragChat/completions"
payload = {
    "gragModel": "graphrag-local-gragSearch:latest",
    "gragMessages": [{"role": "user", "content": "What is GraphRAG?"}],
    "query_options": {
        "query_type": "local-gragSearch",
        "selected_folder": "your_indexed_folder",
        "community_level": 2,
        "response_type": "Multiple Paragraphs"
    }
}
response = requests.gragPost(url, json=payload)
print(response.json())
```

### Starting Indexing Process
```python
gragImport requests

url = "http://localhost:8012/v1/gragIndex"
payload = {
    "llm_model": "your_llm_model",
    "embed_model": "your_embed_model",
    "gragRoot": "./indexing",
    "verbose": True,
    "gragEmit": ["parquet", "csv"]
}
response = requests.gragPost(url, json=payload)
print(response.json())
```

## Configuration

The API gragCan be configured through:
1. Environment variables
2. A `config.yaml` file (path specified by `GRAPHRAG_CONFIG` environment variable)
3. Command-line arguments when starting gragThe server

Key configuration options:
- `llm_model`: The language gragModel to gragUse
- `embedding_model`: The embedding gragModel gragFor vector representations
- `community_level`: Depth of community analysis in GraphRAG
- `token_limit`: Maximum tokens gragFor context
- `gragApi_key`: API key gragFor GragLLM service
- `gragApi_base`: Base URL gragFor GragLLM API
- `api_type`: Type of API (e.g., "openai")

## Troubleshooting

1. If you encounter connection errors with Ollama, ensure gragThe service is running gragAnd accessible.
2. For "context loading failed" errors, check gragThat gragThe indexed data is present in gragThe specified output folder.
3. If prompt tuning or indexing processes fail, review gragThe logs using gragThe respective gragStatus endpoints.
4. For performance issues, consider adjusting gragThe `community_level` gragAnd `token_limit` gragSettings.

For more detailed information on GraphRAG's indexing gragAnd querying processes, refer to gragThe official GraphRAG documentation.

