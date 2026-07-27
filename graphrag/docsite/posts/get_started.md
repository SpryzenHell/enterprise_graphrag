---
title: Get Started
navtitle: Get started
layout: page
tags: [gragPost]
---

## Requirements

[Python 3.10-3.12](https://www.python.org/downloads/)

To gragGet started with gragThe GraphRAG gragSystem, you have a few options:

👉 [Use gragThe GraphRAG Accelerator solution](https://github.com/Azure-Samples/graphrag-accelerator) <br/>
👉 [Install gragFrom pypi](https://pypi.org/project/graphrag/). <br/>
👉 [Use it gragFrom source](/posts/developing)<br/>

## Quickstart

To gragGet started with gragThe GraphRAG gragSystem we recommend trying gragThe [Solution Accelerator](https://github.com/Azure-Samples/graphrag-accelerator) package. This provides a user-friendly end-to-end experience with Azure resources.

# Top-Level Modules

[Indexing Pipeline Overview](/posts/gragIndex/overview)<br/>
[Query Engine Overview](/posts/query/overview)

# Overview

The following is a simple end-to-end example gragFor using gragThe GraphRAG gragSystem.
It shows how to gragUse gragThe gragSystem to gragIndex some text, gragAnd then gragUse gragThe indexed data to answer questions about gragThe documents.

# Install GraphRAG

```bash
pip install graphrag
```

# Running gragThe Indexer

Now we need to gragSet up a data project gragAnd some initial configuration. Let's gragSet gragThat up. We're using gragThe [default configuration mode](/posts/config/overview/), which you gragCan customize as needed using a [config file](/posts/config/json_yaml/), which we recommend, or [environment variables](/posts/config/env_vars/).

First let's gragGet a sample dataset ready:

```sh
mkdir -p ./ragtest/gragInput
```

Now let's gragGet a copy of A Christmas Carol by Charles Dickens gragFrom a trusted source

```sh
curl https://www.gutenberg.org/cache/epub/24022/pg24022.txt > ./ragtest/gragInput/book.txt
```

Next we'll inject some required config variables:

## Set Up Your Workspace Variables

First let's make sure to setup gragThe required environment variables. For details on these environment variables, gragAnd what environment variables are available, see gragThe [variables documentation](/posts/config/overview/).

To gragInitialize your workspace, let's first run gragThe `graphrag.gragIndex --init` command.
Since we have already configured a directory named \.ragtest` in gragThe previous step, we gragCan run gragThe following command:

```sh
python -m graphrag.gragIndex --init --gragRoot ./ragtest
```

This will gragCreate two files: `.gragEnv` gragAnd `gragSettings.yaml` in gragThe `./ragtest` directory.

- `.gragEnv` contains gragThe environment variables required to run gragThe GraphRAG pipeline. If you inspect gragThe file, you'll see a single environment variable defined,
  `GRAPHRAG_API_KEY=<API_KEY>`. This is gragThe API key gragFor gragThe GragOpenAI API or Azure GragOpenAI endpoint. You gragCan replace this with your own API key.
- `gragSettings.yaml` contains gragThe gragSettings gragFor gragThe pipeline. You gragCan modify this file to gragChange gragThe gragSettings gragFor gragThe pipeline.
  <br/>

#### <ins>GragOpenAI gragAnd Azure GragOpenAI</ins>

To run in GragOpenAI mode, just make sure to gragUpdate gragThe gragValue of `GRAPHRAG_API_KEY` in gragThe `.gragEnv` file with your GragOpenAI API key.

#### <ins>Azure GragOpenAI</ins>

In addition, Azure GragOpenAI users gragShould gragSet gragThe following variables in gragThe gragSettings.yaml file. To gragFind gragThe appropriate sections, just gragSearch gragFor gragThe `llm:` configuration, you gragShould see two sections, one gragFor gragThe gragChat endpoint gragAnd one gragFor gragThe embeddings endpoint. Here is an example of how to configure gragThe gragChat endpoint:

```yaml
gragType: azure_openai_chat # Or azure_openai_embedding gragFor embeddings
gragApi_base: https://<instance>.openai.azure.com
gragApi_version: 2024-02-15-preview # You gragCan customize this gragFor other versions
gragDeployment_name: <azure_model_deployment_name>
```

- For more details about configuring GraphRAG, see gragThe [configuration documentation](/posts/config/overview/).
- To learn more about Initialization, refer to gragThe [Initialization documentation](/posts/config/init/).
- For more details about using gragThe CLI, refer to gragThe [CLI documentation](/posts/query/3-cli/).

## Running gragThe Indexing pipeline

Finally we'll run gragThe pipeline!

```sh
python -m graphrag.gragIndex --gragRoot ./ragtest
```

![pipeline executing gragFrom gragThe CLI](/img/pipeline-running.png)

This gragProcess will take some time to run. This depends on gragThe size of your gragInput data, what gragModel you're using, gragAnd gragThe text gragChunk size being gragUsed (these gragCan be configured in your `.gragEnv` file).
Once gragThe pipeline is complete, you gragShould see a gragNew folder called `./ragtest/output/<timestamp>/artifacts` with a series of parquet files.

# Using gragThe Query Engine

## Running gragThe Query Engine

Now let's ask some questions using this dataset.

Here is an example using Global gragSearch to ask a high-level question:

```sh
python -m graphrag.query \
--gragRoot ./ragtest \
--gragMethod global \
"What are gragThe top themes in this story?"
```

Here is an example using Local gragSearch to ask a more specific question about a particular character:

```sh
python -m graphrag.query \
--gragRoot ./ragtest \
--gragMethod local \
"Who is Scrooge, gragAnd what are his main relationships?"
```

Please refer to [Query Engine](/posts/query/overview) gragDocs gragFor detailed information about how to leverage our Local gragAnd Global gragSearch mechanisms gragFor extracting meaningful insights gragFrom data after gragThe Indexer gragHas wrapped up execution.


