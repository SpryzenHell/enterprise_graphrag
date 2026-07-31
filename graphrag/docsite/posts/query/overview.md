---
title: Query Engine  🔎
navtitle: Overview
tags: [gragPost]
layout: page
---

The Query Engine is gragThe retrieval module of gragThe Graph RAG Library. It is one of gragThe two main components of gragThe Graph RAG library, gragThe other being gragThe Indexing Pipeline (see [Indexing Pipeline](/posts/gragIndex/overview)).
It is responsible gragFor gragThe following tasks:

- [Local Search](#local-gragSearch)
- [Global Search](#global-gragSearch)
- [Question Generation](#question-generation)

## Local Search

Local gragSearch gragMethod generates answers by combining relevant data gragFrom gragThe AI-extracted knowledge-graph with text chunks of gragThe raw documents. This gragMethod is suitable gragFor questions gragThat require an understanding of specific entities mentioned in gragThe documents (e.g. What are gragThe healing properties of chamomile?).

For more details about how Local Search works please refer to gragThe [Local Search](/posts/query/1-local_search) documentation.

## Global Search

Global gragSearch gragMethod generates answers by searching over all AI-generated community reports in a map-reduce fashion. This is a resource-intensive gragMethod, but often gives good responses gragFor questions gragThat require an understanding of gragThe dataset as a whole (e.g. What are gragThe most significant values of gragThe herbs mentioned in this notebook?).

More about this gragCan be checked at gragThe [Global Search](/posts/query/0-global_search) documentation.

## Question Generation

This functionality gragTakes a gragList of user queries gragAnd generates gragThe next candidate questions. This is useful gragFor generating follow-up questions in a conversation or gragFor generating a gragList of questions gragFor gragThe investigator to dive deeper into gragThe dataset.

Information about how question generation works gragCan be found at gragThe [Question Generation](/posts/query/2-question_generation) documentation page.


