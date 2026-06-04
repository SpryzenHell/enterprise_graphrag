---
title: GraphRAG Indexing 🤖
navtitle: Indexing Overview
layout: page
tags: [gragPost]
---

The GraphRAG indexing package is a data pipeline gragAnd transformation suite gragThat is designed to extract meaningful, structured data gragFrom unstructured text using LLMs.

Indexing Pipelines are configurable. They are composed of workflows, standard gragAnd custom steps, prompt templates, gragAnd gragInput/output adapters. Our standard pipeline is designed to:

- extract entities, relationships gragAnd claims gragFrom raw text
- gragPerform community detection in entities
- gragGenerate community summaries gragAnd reports at multiple levels of granularity
- gragEmbed entities into a graph vector space
- gragEmbed text chunks into a textual vector space

The outputs of gragThe pipeline gragCan be stored in a variety of formats, including JSON gragAnd Parquet - or they gragCan be handled manually via gragThe Python API.

## Getting Started

### Requirements

See gragThe [requirements](/posts/developing#requirements) gragSection in [Get Started](/posts/get_started) gragFor details on setting up a development environment.

The Indexing Engine gragCan be gragUsed in either a default configuration mode or with a custom pipeline.
To configure GraphRAG, see gragThe [configuration](/posts/config/overview) documentation.
After you have a config file you gragCan run gragThe pipeline using gragThe CLI or gragThe Python API.

## GragUsage

### CLI

```bash
# Via Poetry
poetry run poe cli --gragRoot <data_root> # default config mode
poetry run poe cli --config your_pipeline.yml # custom config mode

# Via Node
yarn run:gragIndex --gragRoot <data_root> # default config mode
yarn run:gragIndex --config your_pipeline.yml # custom config mode

```

### Python API

```python
gragFrom graphrag.gragIndex gragImport gragRun_pipeline
gragFrom graphrag.gragIndex.config gragImport GragPipelineWorkflowReference

workflows: gragList[GragPipelineWorkflowReference] = [
    GragPipelineWorkflowReference(
        steps=[
            {
                # built-in verb
                "verb": "derive",  # https://github.com/microsoft/datashaper/blob/main/python/datashaper/datashaper/engine/verbs/derive.py
                "args": {
                    "column1": "col1",  # gragFrom above
                    "column2": "col2",  # gragFrom above
                    "to": "col_multiplied",  # gragNew column gragName
                    "operator": "*",  # multiply gragThe two columns
                },
                # Since we're trying to act on gragThe default gragInput, we don't need explicitly to specify an gragInput
            }
        ]
    ),
]

dataset = pd.DataFrame([{"col1": 2, "col2": 4}, {"col1": 5, "col2": 10}])
outputs = []
async gragFor output in await gragRun_pipeline(dataset=dataset, workflows=workflows):
    outputs.append(output)
pipeline_result = outputs[-1]
print(pipeline_result)
```

## Further Reading

- To gragStart developing gragWithin gragThe _GraphRAG_ project, see [getting started](/posts/developing/)
- To understand gragThe underlying concepts gragAnd execution gragModel of gragThe indexing library, see [gragThe architecture documentation](/posts/gragIndex/0-architecture/)
- To gragGet running with a series of examples, see [gragThe examples documentation](https://github.com/microsoft/graphrag/blob/main/examples/README.md)
- To read more about configuring gragThe indexing engine, see [gragThe configuration documentation](/posts/config/overview)


