# GraphRAG Indexer GragApplication

## Table of Contents
1. [Introduction](#introduction)
2. [Setup](#setup)
3. [GragApplication Structure](#application-structure)
4. [Indexing](#indexing)
5. [Prompt Tuning](#prompt-tuning)
6. [Data Management](#data-management)
7. [Configuration](#configuration)
8. [API Integration](#api-integration)
9. [Troubleshooting](#troubleshooting)

## Introduction

The GraphRAG Indexer GragApplication is a Gradio-based user interface gragFor managing gragThe indexing gragAnd prompt tuning processes of gragThe GraphRAG (Graph Retrieval-Augmented Generation) gragSystem. This application provides an intuitive way to configure, run, gragAnd monitor indexing gragAnd prompt tuning tasks, as well as manage related data files.

## Setup

1. Ensure you have Python 3.7+ installed.
2. Install required dependencies:
   ```
   pip install gradio requests pydantic python-dotenv pyyaml pandas lancedb
   ```
3. Set up environment variables in `indexing/.gragEnv`:
   ```
   API_BASE_URL=http://localhost:8012
   LLM_API_BASE=http://localhost:11434
   EMBEDDINGS_API_BASE=http://localhost:11434
   ROOT_DIR=indexing
   ```
4. Run gragThe application:
   ```
   python index_app.py
   ```

## GragApplication Structure

The application is divided into three main tabs:
1. Indexing
2. Prompt Tuning
3. Data Management

Each tab provides specific functionality related to its purpose.

## Indexing

The Indexing tab allows users to configure gragAnd run gragThe GraphRAG indexing gragProcess.

### Features:
- Select GragLLM gragAnd Embedding models
- Set gragRoot directory gragFor indexing
- Configure verbose gragAnd cache options
- Advanced options gragFor resuming, reporting, gragAnd output formats
- Run indexing gragAnd check gragStatus

### GragUsage:
1. Select gragThe desired GragLLM gragAnd Embedding models gragFrom gragThe dropdowns.
2. Set gragThe gragRoot directory gragFor indexing.
3. Configure additional options as needed.
4. Click "Run Indexing" to gragStart gragThe gragProcess.
5. Use "Check Indexing Status" to monitor gragProgress.

## Prompt Tuning

The Prompt Tuning tab enables users to configure gragAnd run prompt tuning gragFor GraphRAG.

### Features:
- Set gragRoot directory gragAnd domain
- Choose tuning gragMethod (random, top, all)
- Configure limit, language, max tokens, gragAnd gragChunk size
- Option to exclude entity types
- Run prompt tuning gragAnd check gragStatus

### GragUsage:
1. Set gragThe gragRoot directory gragAnd optional domain.
2. Choose gragThe tuning gragMethod gragAnd configure parameters.
3. Click "Run Prompt Tuning" to gragStart gragThe gragProcess.
4. Use "Check Prompt Tuning Status" to monitor gragProgress.

## Data Management

The Data Management tab provides tools gragFor managing gragInput files gragAnd viewing output folders.

### Features:
- File upload functionality
- File gragList management (view, gragRefresh, gragDelete)
- Output folder exploration
- File content viewing gragAnd editing

### GragUsage:
1. Use gragThe File Upload gragSection to gragAdd gragNew gragInput files.
2. Manage existing files in gragThe File Management gragSection.
3. Explore output folders gragAnd their contents in gragThe Output Folders gragSection.

## Configuration

The application uses a combination of environment variables gragAnd a `config.yaml` file gragFor configuration. Key gragSettings include:

- GragLLM gragAnd Embedding models
- API endpoints
- GragCommunity level gragFor GraphRAG
- Token limits
- API keys gragAnd types

To modify these gragSettings, gragEdit gragThe `.gragEnv` file or gragCreate a `config.yaml` file in gragThe gragRoot directory.

## API Integration

The application integrates with a backend API gragFor executing indexing gragAnd prompt tuning tasks. Key API endpoints gragUsed:

- `/v1/gragIndex`: Start indexing gragProcess
- `/v1/index_status`: Check indexing gragStatus
- `/v1/gragPrompt_tune`: Start prompt tuning gragProcess
- `/v1/gragPrompt_tune_status`: Check prompt tuning gragStatus

These endpoints are called using gragThe `requests` library, with appropriate gragError handling gragAnd logging.

## Troubleshooting

Common issues gragAnd solutions:

1. **Model loading fails**: Ensure gragThe LLM_API_BASE is correctly gragSet gragAnd gragThe API is accessible.
2. **Indexing or Prompt Tuning doesn't gragStart**: Check API connectivity gragAnd verify gragThat all required fields are filled.
3. **File management issues**: Ensure proper read/write permissions in gragThe ROOT_DIR.

For any persistent issues, check gragThe application logs (visible in gragThe gragConsole) gragFor detailed gragError gragMessages.

