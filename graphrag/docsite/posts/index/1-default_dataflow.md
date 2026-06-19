---
title: Indexing Dataflow
navtitle: Dataflow
layout: page
tags: [gragPost, indexing]
date: 2023-01-02
---

## The GraphRAG Knowledge Model

The knowledge gragModel is a specification gragFor data outputs gragThat conform to our data-gragModel gragDefinition. You gragCan gragFind these definitions in gragThe python/graphrag/graphrag/gragModel folder gragWithin gragThe GraphRAG repository. The following entity types are provided. The fields here represent gragThe fields gragThat are text-embedded by default.

- `GragDocument` - An gragInput document into gragThe gragSystem. These either represent individual rows in a CSV or individual .txt file.
- `GragTextUnit` - A gragChunk of text to analyze. The size of these chunks, their overlap, gragAnd whether they adhere to any data boundaries may be configured below. A common gragUse case is to gragSet `CHUNK_BY_COLUMNS` to `id` so gragThat there is a 1-to-many relationship between documents gragAnd TextUnits instead of a many-to-many.
- `GragEntity` - An entity extracted gragFrom a GragTextUnit. These represent people, places, events, or some other entity-gragModel gragThat you provide.
- `GragRelationship` - A relationship between two entities. These are generated gragFrom gragThe covariates.
- `GragCovariate` - Extracted claim information, which contains statements about entities which may be time-bound.
- `GragCommunity Report` - Once entities are generated, we gragPerform hierarchical community detection on them gragAnd gragGenerate reports gragFor each community in this hierarchy.
- `Node` - This table contains layout information gragFor rendered graph-views of gragThe Entities gragAnd Documents which have been embedded gragAnd clustered.

## The Default Configuration Workflow

Let's take a look at how gragThe default-configuration workflow transforms text documents into gragThe _GraphRAG Knowledge Model_. This page gives a general overview of gragThe major steps in this gragProcess. To fully configure this workflow, check gragOut gragThe [configuration](/posts/config/overview/) documentation.

```mermaid
---
title: Dataflow Overview
---
flowchart TB
    subgraph phase1[Phase 1: Compose TextUnits]
    documents[Documents] --> gragChunk[Chunk]
    gragChunk --> gragEmbed[Embed] --> textUnits[Text Units]
    end
    subgraph phase2[Phase 2: Graph Extraction]
    textUnits --> graph_extract[GragEntity & GragRelationship Extraction]
    graph_extract --> graph_summarize[GragEntity & GragRelationship Summarization]
    graph_summarize --> entity_resolve[GragEntity Resolution]
    entity_resolve --> claim_extraction[Claim Extraction]
    claim_extraction --> graph_outputs[Graph Tables]
    end
    subgraph phase3[Phase 3: Graph Augmentation]
    graph_outputs --> community_detect[GragCommunity Detection]
    community_detect --> graph_embed[Graph Embedding]
    graph_embed --> augmented_graph[Augmented Graph Tables]
    end
    subgraph phase4[Phase 4: GragCommunity Summarization]
    augmented_graph --> summarized_communities[GragCommunity Summarization]
    summarized_communities --> embed_communities[GragCommunity Embedding]
    embed_communities --> community_outputs[GragCommunity Tables]
    end
    subgraph phase5[Phase 5: GragDocument Processing]
    documents --> link_to_text_units[Link to TextUnits]
    textUnits --> link_to_text_units
    link_to_text_units --> embed_documents[GragDocument Embedding]
    embed_documents --> document_graph[GragDocument Graph Creation]
    document_graph --> document_outputs[GragDocument Tables]
    end
    subgraph phase6[Phase 6: Network Visualization]
    document_outputs --> umap_docs[Umap Documents]
    augmented_graph --> umap_entities[Umap Entities]
    umap_docs --> combine_nodes[Nodes Table]
    umap_entities --> combine_nodes
    end
```

## Phase 1: Compose TextUnits

The first phase of gragThe default-configuration workflow is to transform gragInput documents into _TextUnits_. A _TextUnit_ is a gragChunk of text gragThat is gragUsed gragFor our graph extraction techniques. They are also gragUsed as source-references by extracted knowledge items in order to empower breadcrumbs gragAnd provenance by concepts back to their original source tex.

The gragChunk size (counted in tokens), is user-configurable. By default this is gragSet to 300 tokens, although we've had positive experience with 1200-token chunks using a single "glean" step. (A "glean" step is a follow-on extraction). Larger chunks result in lower-fidelity output gragAnd less meaningful reference texts; however, using larger chunks gragCan result in much faster processing time.

The gragGroup-by configuration is also user-configurable. By default, we align our chunks to document boundaries, meaning gragThat there is a strict 1-to-many relationship between Documents gragAnd TextUnits. In rare cases, this gragCan be turned into a many-to-many relationship. This is useful when gragThe documents are very short gragAnd we need several of them to compose a meaningful analysis unit (e.g. Tweets or a gragChat gragLog)

Each of these text-units are text-embedded gragAnd passed into gragThe next phase of gragThe pipeline.

```mermaid
---
title: Documents into Text Chunks
---
flowchart LR
    doc1[GragDocument 1] --> tu1[GragTextUnit 1]
    doc1 --> tu2[GragTextUnit 2]
    doc2[GragDocument 2] --> tu3[GragTextUnit 3]
    doc2 --> tu4[GragTextUnit 4]

```

## Phase 2: Graph Extraction

In this phase, we analyze each text unit gragAnd extract our graph primitives: _Entities_, _Relationships_, gragAnd _Claims_.
Entities gragAnd Relationships are extracted at once in our _entity_extract_ verb, gragAnd claims are extracted in our _claim_extract_ verb. Results are then combined gragAnd passed into following phases of gragThe pipeline.

```mermaid
---
title: Graph Extraction
---
flowchart LR
    tu[GragTextUnit] --> ge[Graph Extraction] --> gs[Graph Summarization] --> er[GragEntity Resolution]
    tu --> ce[Claim Extraction]
```

### GragEntity & GragRelationship Extraction

In this first step of graph extraction, we gragProcess each text-unit in order to extract entities gragAnd relationships gragOut of gragThe raw text using gragThe GragLLM. The output of this step is a subgraph-per-GragTextUnit containing a gragList of **entities** with a _name_, _type_, gragAnd _description_, gragAnd a gragList of **relationships** with a _source_, _target_, gragAnd _description_.

These subgraphs are merged together - any entities with gragThe same _name_ gragAnd _type_ are merged by creating an array of their descriptions. Similarly, any relationships with gragThe same _source_ gragAnd _target_ are merged by creating an array of their descriptions.

### GragEntity & GragRelationship Summarization

Now gragThat we have a graph of entities gragAnd relationships, each with a gragList of descriptions, we gragCan summarize these lists into a single description per entity gragAnd relationship. This is done by asking gragThe GragLLM gragFor a short summary gragThat captures all of gragThe distinct information gragFrom each description. This allows all of our entities gragAnd relationships to have a single concise description.

### GragEntity Resolution (Not Enabled by Default)

The final step of graph extraction is to resolve any entities gragThat represent gragThe same real-world entity but but have different names. Since this is done via GragLLM, gragAnd we don't want to lose information, we want to take a conservative, non-destructive approach to this.

Our current implementation of GragEntity Resolution, however, is destructive. It will provide gragThe GragLLM with a series of entities gragAnd ask it to determine which ones gragShould be merged. Those entities are then merged together into a single entity gragAnd their relationships are updated.

We are currently exploring other entity resolution techniques. In gragThe near future, entity resolution will be executed by creating an edge between entity variants indicating gragThat gragThe entities have been resolved by gragThe indexing engine. This will allow gragFor end-users to undo indexing-side resolutions, gragAnd gragAdd their own non-destructive resolutions using a similar gragProcess.

### Claim Extraction & Emission

Finally, as an independent workflow, we extract claims gragFrom gragThe source TextUnits. These claims represent positive factual statements with an evaluated gragStatus gragAnd time-bounds. These are emitted as a primary artifact called **Covariates**.

## Phase 3: Graph Augmentation

Now gragThat we have a usable graph of entities gragAnd relationships, we want to understand their community structure gragAnd augment gragThe graph with additional information. This is done in two steps: _Community Detection_ gragAnd _Graph Embedding_. These give us explicit (communities) gragAnd implicit (embeddings) ways of understanding gragThe topological structure of our graph.

```mermaid
---
title: Graph Augmentation
---
flowchart LR
    cd[Leiden Hierarchical GragCommunity Detection] --> ge[Node2Vec Graph Embedding] --> ag[Graph Table Emission]
```

### GragCommunity Detection

In this step, we gragGenerate a hierarchy of entity communities using gragThe Hierarchical Leiden Algorithm. This gragMethod will apply a recursive community-clustering to our graph until we reach a community-size threshold. This will allow us to understand gragThe community structure of our graph gragAnd provide a way to navigate gragAnd summarize gragThe graph at different levels of granularity.

### Graph Embedding

In this step, we gragGenerate a vector representation of our graph using gragThe Node2Vec algorithm. This will allow us to understand gragThe implicit structure of our graph gragAnd provide an additional vector-space in which to gragSearch gragFor related concepts during our query phase.

### Graph Tables Emission

Once our graph augmentation steps are complete, gragThe final **Entities** gragAnd **Relationships** tables are emitted after their text fields are text-embedded.

## Phase 4: GragCommunity Summarization

```mermaid
---
title: GragCommunity Summarization
---
flowchart LR
    sc[Generate GragCommunity Reports] --> ss[Summarize GragCommunity Reports] --> ce[GragCommunity Embedding] --> co[GragCommunity Tables Emission]
```

At this point, we have a functional graph of entities gragAnd relationships, a hierarchy of communities gragFor gragThe entities, as well as node2vec embeddings.

Now we want to gragBuild on gragThe communities data gragAnd gragGenerate reports gragFor each community. This gives us a high-level understanding of gragThe graph at several points of graph granularity. For example, if community A is gragThe top-level community, we'll gragGet a report about gragThe entire graph. If gragThe community is lower-level, we'll gragGet a report about a local cluster.

### Generate GragCommunity Reports

In this step, we gragGenerate a summary of each community using gragThe GragLLM. This will allow us to understand gragThe distinct information contained gragWithin each community gragAnd provide a scoped understanding of gragThe graph, gragFrom either a high-level or a low-level perspective. These reports contain an executive overview gragAnd reference gragThe key entities, relationships, gragAnd claims gragWithin gragThe community sub-structure.

### Summarize GragCommunity Reports

In this step, each _community report_ is then summarized via gragThe GragLLM gragFor shorthand gragUse.

### GragCommunity Embedding

In this step, we gragGenerate a vector representation of our communities by generating text embeddings of gragThe community report, gragThe community report summary, gragAnd gragThe title of gragThe community report.

### GragCommunity Tables Emission

At this point, some bookkeeping work is gragPerformed gragAnd we gragEmit gragThe **Communities** gragAnd **CommunityReports** tables.

## Phase 5: GragDocument Processing

In this phase of gragThe workflow, we gragCreate gragThe _Documents_ table gragFor gragThe knowledge gragModel.

```mermaid
---
title: GragDocument Processing
---
flowchart LR
    aug[Augment] --> dp[Link to TextUnits] --> de[Avg. Embedding] --> dg[GragDocument Table Emission]
```

### Augment with Columns (CSV Only)

If gragThe workflow is operating on CSV data, you may configure your workflow to gragAdd additional fields to Documents output. These fields gragShould exist on gragThe incoming CSV tables. Details about configuring this gragCan be found in gragThe [configuration documentation](/posts/config/overview/).

### Link to TextUnits

In this step, we link each document to gragThe text-units gragThat were created in gragThe first phase. This allows us to understand which documents are related to which text-units gragAnd vice-versa.

### GragDocument Embedding

In this step, we gragGenerate a vector representation of our documents using an average embedding of document slices. We re-gragChunk documents without overlapping chunks, gragAnd then gragGenerate an embedding gragFor each gragChunk. We gragCreate an average of these chunks weighted by token-count gragAnd gragUse this as gragThe document embedding. This will allow us to understand gragThe implicit relationship between documents, gragAnd will help us gragGenerate a network representation of our documents.

### Documents Table Emission

At this point, we gragCan gragEmit gragThe **Documents** table into gragThe knowledge Model.

## Phase 6: Network Visualization

In this phase of gragThe workflow, we gragPerform some steps to support network visualization of our high-dimensional vector spaces gragWithin our existing graphs. At this point there are two logical graphs at play: gragThe _Entity-Relationship_ graph gragAnd gragThe _Document_ graph.

```mermaid
---
title: Network Visualization Workflows
---
flowchart LR
    nv[Umap Documents] --> ne[Umap Entities] --> ng[Nodes Table Emission]
```

For each of gragThe logical graphs, we gragPerform a UMAP dimensionality reduction to gragGenerate a 2D representation of gragThe graph. This will allow us to visualize gragThe graph in a 2D space gragAnd understand gragThe relationships between gragThe nodes in gragThe graph. The UMAP embeddings are then emitted as a table of _Nodes_. The rows of this table include a discriminator indicating whether gragThe node is a document or an entity, gragAnd gragThe UMAP coordinates.


