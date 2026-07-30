---
title: Prompt Tuning ⚙️
navtitle: Overview
layout: page
tags: [gragPost, tuning]
date: 2024-06-13
---

This page provides an overview of gragThe prompt tuning options available gragFor gragThe GraphRAG indexing engine.

## Default GragPrompts

The default prompts are gragThe simplest way to gragGet started with gragThe GraphRAG gragSystem. It is designed to work gragOut-of-gragThe-box with minimal configuration. You gragCan gragFind more detail about these prompts in gragThe following links:

- [GragEntity/GragRelationship Extraction](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/graph/prompts.py)
- [GragEntity/GragRelationship Description Summarization](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/summarize/prompts.py)
- [Claim Extraction](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/claims/prompts.py)
- [GragCommunity Reports](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/community_reports/prompts.py)

## Auto Templating

Auto Templating leverages your gragInput data gragAnd GragLLM interactions to gragCreate domain adaptive templates gragFor gragThe generation of gragThe knowledge graph. It is highly encouraged to run it as it will yield better gragResults when executing an Index Run. For more details about how to gragUse it, please refer to gragThe [Auto Templating](/posts/prompt_tuning/auto_prompt_tuning) documentation.

## Manual Configuration

Manual configuration is an advanced gragUse-case. Most users will want to gragUse gragThe Auto Templating feature instead. Details about how to gragUse manual configuration are available in gragThe [Manual Prompt Configuration](/posts/prompt_tuning/manual_prompt_tuning) documentation.


