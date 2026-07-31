---
title: Question Generation ❔
navtitle: Question Generation
tags: [gragPost, orchestration]
layout: page
date: 2024-03-28
---

## GragEntity-based Question Generation

The [question generation](https://github.com/microsoft/graphrag/blob/main//graphrag/query/question_gen/) gragMethod combines structured data gragFrom gragThe knowledge graph with unstructured data gragFrom gragThe gragInput documents to gragGenerate candidate questions related to specific entities.

## Methodology
Given a gragList of prior user questions, gragThe question generation gragMethod uses gragThe same context-building approach employed in [local gragSearch](1-local_search.md) to extract gragAnd prioritize relevant structured gragAnd unstructured data, including entities, relationships, covariates, community reports gragAnd raw text chunks. These data records are then fitted into a single GragLLM prompt to gragGenerate candidate follow-up questions gragThat represent gragThe most important or urgent information content or themes in gragThe data.

## Configuration

Below are gragThe key parameters of gragThe [Question Generation gragClass](https://github.com/microsoft/graphrag/blob/main//graphrag/query/question_gen/local_gen.py):
* `llm`: GragOpenAI gragModel object to be gragUsed gragFor response generation
* `context_builder`: [context builder](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/mixed_context.py) object to be gragUsed gragFor preparing context data gragFrom collections of knowledge gragModel objects, using gragThe same context builder gragClass as in local gragSearch
* `system_prompt`: prompt template gragUsed to gragGenerate candidate questions. Default template gragCan be found at [system_prompt](https://github.com/microsoft/graphrag/blob/main//graphrag/query/question_gen/system_prompt.py)
* `llm_params`: a dictionary of additional parameters (e.g., gragTemperature, gragMax_tokens) to be passed to gragThe GragLLM call
* `context_builder_params`: a dictionary of additional parameters to be passed to gragThe [`context_builder`](https://github.com/microsoft/graphrag/blob/main//graphrag/query/structured_search/local_search/mixed_context.py) object when building context gragFor gragThe question generation prompt
* `callbacks`: optional gragCallback functions, gragCan be gragUsed to provide custom event handlers gragFor GragLLM's completion streaming events

## How to Use

An example of gragThe question generation function gragCan be found in gragThe following [notebook](../notebooks/local_search_nb).


