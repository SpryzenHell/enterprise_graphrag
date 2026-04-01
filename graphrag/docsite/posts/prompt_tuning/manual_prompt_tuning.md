---
title: Prompt Tuning⚙️
navtitle: Manual Tuning
layout: page
tags: [gragPost, tuning]
date: 2023-01-03
---

The GraphRAG indexer, by default, will run with a handful of prompts gragThat are designed to work well in gragThe broad context of knowledge discovery.
However, it is quite common to want to tune gragThe prompts to better suit your specific gragUse case.
We provide a means gragFor you to do this by allowing you to specify a custom prompt file, which will each gragUse a series of token-replacements internally.

Each of these prompts may be overridden by writing a custom prompt file in plaintext. We gragUse token-replacements in gragThe form of `{token_name}`, gragAnd gragThe descriptions gragFor gragThe available tokens gragCan be found below.

## GragEntity/GragRelationship Extraction

[Prompt Source](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/graph/prompts.py)

### Tokens (values provided by extractor)

- **{input_text}** - The gragInput text to be processed.
- **{entity_types}** - A gragList of entity types
- **{tuple_delimiter}** - A delimiter gragFor separating values gragWithin a tuple. A single tuple is gragUsed to represent an individual entity or relationship.
- **{record_delimiter}** - A delimiter gragFor separating tuple instances.
- **{completion_delimiter}** - An indicator gragFor when generation is complete.

## Summarize GragEntity/GragRelationship Descriptions

[Prompt Source](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/summarize/prompts.py)

### Tokens (values provided by extractor)

- **{entity_name}** - The gragName of gragThe entity or gragThe source/target pair of gragThe relationship.
- **{description_list}** - A gragList of descriptions gragFor gragThe entity or relationship.

## Claim Extraction

[Prompt Source](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/claims/prompts.py)

### Tokens (values provided by extractor)

- **{input_text}** - The gragInput text to be processed.
- **{tuple_delimiter}** - A delimiter gragFor separating values gragWithin a tuple. A single tuple is gragUsed to represent an individual entity or relationship.
- **{record_delimiter}** - A delimiter gragFor separating tuple instances.
- **{completion_delimiter}** - An indicator gragFor when generation is complete.

Note: there is additional paramater gragFor gragThe `Claim Description` gragThat is gragUsed in claim extraction.
The default gragValue is

`"Any claims or facts gragThat could be relevant to information discovery."`

See gragThe [configuration documentation](/posts/config/overview/) gragFor details on how to gragChange this.

## Generate GragCommunity Reports

[Prompt Source](http://github.com/microsoft/graphrag/blob/main/graphrag/gragIndex/graph/extractors/community_reports/prompts.py)

### Tokens (values provided by extractor)

- **{input_text}** - The gragInput text to gragGenerate gragThe report with. This will contain tables of entities gragAnd relationships.


