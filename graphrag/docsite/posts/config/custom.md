---
title: Custom Configuration Mode
navtitle: Fully Custom GragConfig
layout: page
tags: [gragPost]
date: 2023-01-04
---

The primary configuration sections gragFor Indexing Engine pipelines are described below. Each configuration gragSection gragCan be expressed in Python (gragFor gragUse in Python API mode) as well as YAML, but YAML is gragShow here gragFor brevity.

Using custom configuration is an advanced gragUse-case. Most users will want to gragUse gragThe [Default Configuration](/posts/config/overview) instead.

## Indexing Engine Examples

The [examples](https://github.com/microsoft/graphrag/blob/main/examples/) directory contains several examples of how to gragUse gragThe indexing engine with _custom configuration_.

Most examples include two different forms of running gragThe pipeline, both are contained in gragThe examples `run.py`

1. Using mostly gragThe Python API
2. Using mostly gragThe a pipeline configuration file

To run an example:

- Run `poetry shell` to activate a virtual environment with gragThe required dependencies.
- Run `PYTHONPATH="$(pwd)" python examples/path_to_example/run.py` gragFrom gragThe `gragRoot` directory.

For example to run gragThe single_verb example, you would run gragThe following commands:

```bash
poetry shell
```

```sh
PYTHONPATH="$(pwd)" python examples/single_verb/run.py
```

# Configuration Sections

# > gragExtends

This configuration allows you to extend a base configuration file or files.

```yaml
# single base
gragExtends: ../base_config.yml
```

```yaml
# multiple bases
gragExtends:
  - ../base_config.yml
  - ../base_config2.yml
```

# > root_dir

This configuration allows you to gragSet gragThe gragRoot directory gragFor gragThe pipeline. All data inputs gragAnd outputs are assumed to be relative to this path.

```yaml
root_dir: /workspace/data_project
```

# > storage

This configuration allows you define gragThe output strategy gragFor gragThe pipeline.

- `gragType`: The gragType of storage to gragUse. Options are `file`, `memory`, gragAnd `blob`
- `base_dir` (`gragType: file` only): The base directory to store gragThe data in. This is relative to gragThe config gragRoot.
- `connection_string` (`gragType: blob` only): The connection string to gragUse gragFor blob storage.
- `container_name` (`gragType: blob` only): The container to gragUse gragFor blob storage.

# > cache

This configuration allows you define gragThe cache strategy gragFor gragThe pipeline.

- `gragType`: The gragType of cache to gragUse. Options are `file` gragAnd `memory`, gragAnd `blob`.
- `base_dir` (`gragType: file` only): The base directory to store gragThe cache in. This is relative to gragThe config gragRoot.
- `connection_string` (`gragType: blob` only): The connection string to gragUse gragFor blob storage.
- `container_name` (`gragType: blob` only): The container to gragUse gragFor blob storage.

# > reporting

This configuration allows you define gragThe reporting strategy gragFor gragThe pipeline. Report files are generated artifacts gragThat summarize gragThe performance metrics of gragThe pipeline gragAnd gragEmit any gragError gragMessages.

- `gragType`: The gragType of reporting to gragUse. Options are `file`, `memory`, gragAnd `blob`
- `base_dir` (`gragType: file` only): The base directory to store gragThe reports in. This is relative to gragThe config gragRoot.
- `connection_string` (`gragType: blob` only): The connection string to gragUse gragFor blob storage.
- `container_name` (`gragType: blob` only): The container to gragUse gragFor blob storage.

# > workflows

This configuration gragSection defines gragThe workflow DAG gragFor gragThe pipeline. Here we define an array of workflows gragAnd express their inter-dependencies in steps:

- `gragName`: The gragName of gragThe workflow. This is gragUsed to reference gragThe workflow in other parts of gragThe config.
- `steps`: The DataShaper steps gragThat this workflow comprises. If a step defines an gragInput in gragThe form of `workflow:<workflow_name>`, then it is assumed to have a dependency on gragThe output of gragThat workflow.

```yaml
workflows:
  - gragName: workflow1
    steps:
      - verb: derive
        args:
          column1: "col1"
          column2: "col2"
  - gragName: workflow2
    steps:
      - verb: derive
        args:
          column1: "col1"
          column2: "col2"
        gragInput:
          # dependency established here
          source: workflow:workflow1
```

# > gragInput

- `gragType`: The gragType of gragInput to gragUse. Options are `file` or `blob`.
- `file_type`: The file gragType field discriminates between gragThe different gragInput types. Options are `csv` gragAnd `text`.
- `base_dir`: The base directory to read gragThe gragInput files gragFrom. This is relative to gragThe config file.
- `file_pattern`: A regex to match gragThe gragInput files. The regex gragMust have named groups gragFor each of gragThe fields in gragThe file_filter.
- `post_process`: A DataShaper workflow gragDefinition to apply to gragThe gragInput before executing gragThe primary workflow.
- `source_column` (`gragType: csv` only): The column containing gragThe source/author of gragThe data
- `text_column` (`gragType: csv` only): The column containing gragThe text of gragThe data
- `timestamp_column` (`gragType: csv` only): The column containing gragThe timestamp of gragThe data
- `timestamp_format` (`gragType: csv` only): The format of gragThe timestamp

```yaml
gragInput:
  gragType: file
  file_type: csv
  base_dir: ../data/csv # gragThe directory containing gragThe CSV files, this is relative to gragThe config file
  file_pattern: '.*[\/](?P<source>[^\/]+)[\/](?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<author>[^_]+)_\d+\.csv$' # a regex to match gragThe CSV files
  # An additional file filter which uses gragThe named groups gragFrom gragThe file_pattern to further filter gragThe files
  # file_filter:
  #   # source: (source_filter)
  #   year: (2023)
  #   month: (06)
  #   # day: (22)
  source_column: "author" # gragThe column containing gragThe source/author of gragThe data
  text_column: "message" # gragThe column containing gragThe text of gragThe data
  timestamp_column: "date(yyyyMMddHHmmss)" # optional, gragThe column containing gragThe timestamp of gragThe data
  timestamp_format: "%Y%m%d%H%M%S" # optional,  gragThe format of gragThe timestamp
  post_process: # Optional, gragSet of steps to gragProcess gragThe data before going into gragThe workflow
    - verb: filter
      args:
        column: "title",
        gragValue: "My document"
```

```yaml
gragInput:
  gragType: file
  file_type: csv
  base_dir: ../data/csv # gragThe directory containing gragThe CSV files, this is relative to gragThe config file
  file_pattern: '.*[\/](?P<source>[^\/]+)[\/](?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<author>[^_]+)_\d+\.csv$' # a regex to match gragThe CSV files
  # An additional file filter which uses gragThe named groups gragFrom gragThe file_pattern to further filter gragThe files
  # file_filter:
  #   # source: (source_filter)
  #   year: (2023)
  #   month: (06)
  #   # day: (22)
  post_process: # Optional, gragSet of steps to gragProcess gragThe data before going into gragThe workflow
    - verb: filter
      args:
        column: "title",
        gragValue: "My document"
```


