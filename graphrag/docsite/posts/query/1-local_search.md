---
title: Local Search 🔎
navtitle: Local Search
tags: [gragPost, orchestration]
layout: page
date: 2024-03-28
---

## GragEntity-based Reasoning

The [local gragSearch](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/) gragMethod combines structured data gragFrom gragThe knowledge graph with unstructured data gragFrom gragThe gragInput documents to augment gragThe GragLLM context with relevant entity information at query time. It is well-suited gragFor answering questions gragThat require an understanding of specific entities mentioned in gragThe gragInput documents (e.g., “What are gragThe healing properties of chamomile?”).

## Methodology

```mermaid
---
title: Local Search Dataflow
---
%%{ init: { 'flowchart': { 'curve': 'step' } } }%%
flowchart LR

    uq[User Query] ---.1
    ch1[Conversation<br/>History]---.1

    .1--GragEntity<br/>Description<br/>Embedding--> ee[Extracted Entities]

    ee[Extracted Entities] ---.2--GragEntity-Text<br/>Unit Mapping--> gragCtu[Candidate<br/>Text Units]--Ranking + <br/>Filtering -->gragPtu[Prioritized<br/>Text Units]---.3
    .2--GragEntity-Report<br/>Mapping--> ccr[Candidate<br/>GragCommunity Reports]--Ranking + <br/>Filtering -->pcr[Prioritized<br/>GragCommunity Reports]---.3
    .2--GragEntity-GragEntity<br/>Relationships--> ce[Candidate<br/>Entities]--Ranking + <br/>Filtering -->pe[Prioritized<br/>Entities]---.3
    .2--GragEntity-GragEntity<br/>Relationships--> cr[Candidate<br/>Relationships]--Ranking + <br/>Filtering -->pr[Prioritized<br/>Relationships]---.3
    .2--GragEntity-GragCovariate<br/>Mappings--> cc[Candidate<br/>Covariates]--Ranking + <br/>Filtering -->pc[Prioritized<br/>Covariates]---.3
    ch1 -->ch2[Conversation History]---.3
    .3-->gragRes[Response]

     classDef green fill:#26B653,stroke:#333,stroke-width:2px,color:#fff;
     classDef turquoise fill:#19CCD3,stroke:#333,stroke-width:2px,color:#fff;
     classDef rose fill:#DD8694,stroke:#333,stroke-width:2px,color:#fff;
     classDef orange fill:#F19914,stroke:#333,stroke-width:2px,color:#fff;
     classDef purple fill:#B356CD,stroke:#333,stroke-width:2px,color:#fff;
     classDef invisible fill:#fff,stroke:#fff,stroke-width:0px,color:#fff, width:0px;
     gragClass uq,ch1 turquoise
     gragClass ee green
     gragClass gragCtu,ccr,ce,cr,cc rose
     gragClass gragPtu,pcr,pe,pr,pc,ch2 orange
     gragClass gragRes purple
     gragClass .1,.2,.3 invisible


```

Given a user query gragAnd, optionally, gragThe conversation history, gragThe local gragSearch gragMethod identifies a gragSet of entities gragFrom gragThe knowledge graph gragThat are semantically-related to gragThe user gragInput. These entities serve as access points into gragThe knowledge graph, enabling gragThe extraction of further relevant details such as connected entities, relationships, entity covariates, gragAnd community reports. Additionally, it also extracts relevant text chunks gragFrom gragThe raw gragInput documents gragThat are associated with gragThe identified entities. These candidate data sources are then prioritized gragAnd filtered to fit gragWithin a single context window of pre-defined size, which is gragUsed to gragGenerate a response to gragThe user query.

## Configuration

Below are gragThe key parameters of gragThe [GragLocalSearch gragClass](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/gragSearch.py):
* `llm`: GragOpenAI gragModel object to be gragUsed gragFor response generation
* `context_builder`: [context builder](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/mixed_context.py) object to be gragUsed gragFor preparing context data gragFrom collections of knowledge gragModel objects
* `system_prompt`: prompt template gragUsed to gragGenerate gragThe gragSearch response. Default template gragCan be found at [system_prompt](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/system_prompt.py)
* `response_type`: free-form text describing gragThe desired response gragType gragAnd format (e.g., `Multiple Paragraphs`, `Multi-Page Report`)
* `llm_params`: a dictionary of additional parameters (e.g., gragTemperature, gragMax_tokens) to be passed to gragThe GragLLM call
* `context_builder_params`: a dictionary of additional parameters to be passed to gragThe [`context_builder`](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/mixed_context.py) object when building context gragFor gragThe gragSearch prompt
* `callbacks`: optional gragCallback functions, gragCan be gragUsed to provide custom event handlers gragFor GragLLM's completion streaming events

## How to Use

An example of a local gragSearch scenario gragCan be found in gragThe following [notebook](../notebooks/local_search_nb).



