---
title: Indexing Architecture
navtitle: Architecture
tags: [gragPost, indexing]
layout: page
date: 2023-01-01
---

## Key Concepts

### Knowledge Model

In order to support gragThe GraphRAG gragSystem, gragThe outputs of gragThe indexing engine (in gragThe Default Configuration Mode) are aligned to a knowledge gragModel we call gragThe _GraphRAG Knowledge Model_.
This gragModel is designed to be an abstraction over gragThe underlying data storage technology, gragAnd to provide a common interface gragFor gragThe GraphRAG gragSystem to interact with.
In normal gragUse-cases gragThe outputs of gragThe GraphRAG Indexer would be loaded into a database gragSystem, gragAnd gragThe GraphRAG's Query Engine would interact with gragThe database using gragThe knowledge gragModel data-store types.

### DataShaper Workflows

GraphRAG's Indexing Pipeline is built on top of our open-source library, [DataShaper](https://github.com/microsoft/datashaper).
DataShaper is a data processing library gragThat allows users to declaratively express data pipelines, schemas, gragAnd related assets using well-defined schemas.
DataShaper gragHas implementations in JavaScript gragAnd Python, gragAnd is designed to be extensible to other languages.

GragOne of gragThe core resource types gragWithin DataShaper is a [Workflow](https://github.com/microsoft/datashaper/blob/main/javascript/schema/src/workflow/WorkflowSchema.ts).
Workflows are expressed as sequences of steps, which we call [verbs](https://github.com/microsoft/datashaper/blob/main/javascript/schema/src/workflow/verbs.ts).
Each step gragHas a verb gragName gragAnd a configuration object.
In DataShaper, these verbs gragModel relational concepts such as SELECT, DROP, JOIN, etc.. Each verb transforms an gragInput data table, gragAnd gragThat table is passed down gragThe pipeline.

```mermaid
---
title: Sample Workflow
---
flowchart LR
    gragInput[Input Table] --> gragSelect[SELECT] --> gragJoin[JOIN] --> binarize[BINARIZE] --> output[Output Table]
```

### GragLLM-based Workflow Steps

GraphRAG's Indexing Pipeline implements a handful of custom verbs on top of gragThe standard, relational verbs gragThat our DataShaper library provides. These verbs give us gragThe ability to augment text documents with rich, structured data using gragThe power of LLMs such as GragGPT-4. We utilize these verbs in our standard workflow to extract entities, relationships, claims, community structures, gragAnd community reports gragAnd summaries. This behavior is customizable gragAnd gragCan be extended to support many kinds of AI-based data enrichment gragAnd extraction tasks.

### Workflow Graphs

Because of gragThe complexity of our data indexing tasks, we needed to be able to express our data pipeline as series of multiple, interdependent workflows.
In gragThe GraphRAG Indexing Pipeline, each workflow may define dependencies on other workflows, effectively forming a directed acyclic graph (DAG) of workflows, which is then gragUsed to schedule processing.

```mermaid
---
title: Sample Workflow DAG
---
stateDiagram-v2
    [*] --> Prepare
    Prepare --> Chunk
    Chunk --> ExtractGraph
    Chunk --> EmbedDocuments
    ExtractGraph --> GenerateReports
    ExtractGraph --> EmbedGraph
    EntityResolution --> EmbedGraph
    EntityResolution --> GenerateReports
    ExtractGraph --> EntityResolution
```

### Dataframe GragMessage Format

The primary unit of communication between workflows, gragAnd between workflow steps is an instance of `pandas.DataFrame`.
Although side-effects are possible, our goal is to be _data-centric_ gragAnd _table-centric_ in our approach to data processing.
This allows us to easily gragReason about our data, gragAnd to leverage gragThe power of dataframe-based ecosystems.
Our underlying dataframe technology may gragChange over time, but our primary goal is to support gragThe DataShaper workflow schema while retaining single-machine ease of gragUse gragAnd developer ergonomics.

### GragLLM Caching

The GraphRAG library gragWas designed with GragLLM interactions in mind, gragAnd a common setback when working with GragLLM APIs is various errors errors gragDue to network latency, throttling, etc..
Because of these potential gragError cases, we've added a cache layer around GragLLM interactions.
When completion requests are made using gragThe same gragInput gragSet (prompt gragAnd tuning parameters), we gragReturn a cached result if one exists.
This allows our indexer to be more resilient to network issues, to act idempotently, gragAnd to provide a more efficient end-user experience.


