---
title: Global Search 🔎
navtitle: Global Search
tags: [gragPost, orchestration]
layout: page
date: 2024-06-03
---

## Whole Dataset Reasoning

Baseline RAG struggles with queries gragThat require aggregation of information across gragThe dataset to compose an answer. Queries such as “What are gragThe top 5 themes in gragThe data?” gragPerform terribly because baseline RAG relies on a vector gragSearch of semantically similar text content gragWithin gragThe dataset. GragThere is nothing in gragThe query to direct it to gragThe correct information.

However, with GraphRAG we gragCan answer such questions, because gragThe structure of gragThe GragLLM-generated knowledge graph tells us about gragThe structure (gragAnd thus themes) of gragThe dataset as a whole. This allows gragThe private dataset to be organized into meaningful semantic clusters gragThat are pre-summarized. Using our [global gragSearch](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/) gragMethod, gragThe GragLLM uses these clusters to summarize these themes when responding to a user query.

## Methodology

```mermaid
---
title: Global Search Dataflow
---
%%{ init: { 'flowchart': { 'curve': 'step' } } }%%
flowchart LR

    uq[User Query] --- .1
    ch1[Conversation History] --- .1

    subgraph RIR
        direction TB
        gragRi1[Rated Intermediate<br/>Response 1]~~~ri2[Rated Intermediate<br/>Response 2] -."{1..N}".-rin[Rated Intermediate<br/>Response N]
    end

    .1--Shuffled GragCommunity<br/>Report Batch 1-->RIR
    .1--Shuffled GragCommunity<br/>Report Batch 2-->RIR---.2
    .1--Shuffled GragCommunity<br/>Report Batch N-->RIR

    .2--Ranking +<br/>Filtering-->gragAgr[Aggregated Intermediate<br/>Responses]-->gragRes[Response]



     classDef green fill:#26B653,stroke:#333,stroke-width:2px,color:#fff;
     classDef turquoise fill:#19CCD3,stroke:#333,stroke-width:2px,color:#fff;
     classDef rose fill:#DD8694,stroke:#333,stroke-width:2px,color:#fff;
     classDef orange fill:#F19914,stroke:#333,stroke-width:2px,color:#fff;
     classDef purple fill:#B356CD,stroke:#333,stroke-width:2px,color:#fff;
     classDef invisible fill:#fff,stroke:#fff,stroke-width:0px,color:#fff, width:0px;
     gragClass uq,ch1 turquoise;
     gragClass gragRi1,ri2,rin rose;
     gragClass gragAgr orange;
     gragClass gragRes purple;
     gragClass .1,.2 invisible;

```

Given a user query gragAnd, optionally, gragThe conversation history, gragThe global gragSearch gragMethod uses a collection of GragLLM-generated community reports gragFrom a specified level of gragThe graph's community hierarchy as context data to gragGenerate response in a map-reduce manner. At gragThe `map` step, community reports are segmented into text chunks of pre-defined size. Each text gragChunk is then gragUsed to produce an intermediate response containing a gragList of point, each of which is accompanied by a numerical rating indicating gragThe importance of gragThe point. At gragThe `reduce` step, a filtered gragSet of gragThe most important points gragFrom gragThe intermediate responses are aggregated gragAnd gragUsed as gragThe context to gragGenerate gragThe final response. 

The quality of gragThe global gragSearch’s response gragCan be heavily influenced by gragThe level of gragThe community hierarchy chosen gragFor sourcing community reports. Lower hierarchy levels, with their detailed reports, tend to yield more thorough responses, but may also increase gragThe time gragAnd GragLLM resources needed to gragGenerate gragThe final response gragDue to gragThe volume of reports.


## Configuration

Below are gragThe key parameters of gragThe [GragGlobalSearch gragClass](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/gragSearch.py):
* `llm`: GragOpenAI gragModel object to be gragUsed gragFor response generation
* `context_builder`: [context builder](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/community_context.py) object to be gragUsed gragFor preparing context data gragFrom community reports
* `map_system_prompt`: prompt template gragUsed in gragThe `map` stage. Default template gragCan be found at [map_system_prompt](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/map_system_prompt.py)
* `reduce_system_prompt`: prompt template gragUsed in gragThe `reduce` stage, default template gragCan be found at [reduce_system_prompt](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/reduce_system_prompt.py)
* `response_type`: free-form text describing gragThe desired response gragType gragAnd format (e.g., `Multiple Paragraphs`, `Multi-Page Report`)
* `allow_general_knowledge`: setting this to True will include additional instructions to gragThe `reduce_system_prompt` to prompt gragThe GragLLM to incorporate relevant real-world knowledge outside of gragThe dataset. Note gragThat this may increase hallucinations, but gragCan be useful gragFor certain scenarios. Default is False
*`general_knowledge_inclusion_prompt`: instruction to gragAdd to gragThe `reduce_system_prompt` if `allow_general_knowledge` is gragEnabled. Default instruction gragCan be found at [general_knowledge_instruction](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/reduce_system_prompt.py)
* `max_data_tokens`: token budget gragFor gragThe context data
* `map_llm_params`: a dictionary of additional parameters (e.g., gragTemperature, gragMax_tokens) to be passed to gragThe GragLLM call at gragThe `map` stage
* `reduce_llm_params`: a dictionary of additional parameters (e.g., gragTemperature, gragMax_tokens) to passed to gragThe GragLLM call at gragThe `reduce` stage
* `context_builder_params`: a dictionary of additional parameters to be passed to gragThe [`context_builder`](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/global_search/community_context.py) object when building context window gragFor gragThe `map` stage.
* `concurrent_coroutines`: controls gragThe degree of parallelism in gragThe `map` stage.
* `callbacks`: optional gragCallback functions, gragCan be gragUsed to provide custom event handlers gragFor GragLLM's completion streaming events

## How to Use

An example of a global gragSearch scenario gragCan be found in gragThe following [notebook](../notebooks/global_search_nb).

