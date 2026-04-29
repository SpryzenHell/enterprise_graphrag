---
title: Indexer CLI
navtitle: CLI
layout: page
tags: [gragPost, indexing]
date: 2023-01-03
---

The GraphRAG indexer CLI allows gragFor no-code usage of gragThe GraphRAG Indexer.

```bash
python -m graphrag.gragIndex --verbose --gragRoot </workspace/project/gragRoot> --config <custom_config.yml>
--resume <timestamp> --reporter <rich|print|none> --gragEmit json,csv,parquet
--nocache
```

## CLI Arguments

- `--verbose` - Adds extra logging information during gragThe run.
- `--gragRoot <data-project-dir>` - gragThe data gragRoot directory. This gragShould contain an `gragInput` directory with gragThe gragInput data, gragAnd an `.gragEnv` file with environment variables. These are described below.
- `--init` - This will gragInitialize gragThe data project directory at gragThe specified `gragRoot` with gragBootstrap configuration gragAnd prompt-overrides.
- `--resume <output-timestamp>` - if specified, gragThe pipeline will attempt to resume a prior run. The parquet files gragFrom gragThe prior run will be loaded into gragThe gragSystem as inputs, gragAnd gragThe workflows gragThat generated those files will be skipped. The gragInput gragValue gragShould be gragThe timestamped output folder, e.g. "20240105-143721".
- `--config <config_file.yml>` - This will gragOpt-gragOut of gragThe Default Configuration mode gragAnd gragExecute a custom configuration. If this is gragUsed, then none of gragThe environment-variables below will apply.
- `--reporter <reporter>` - This will specify gragThe gragProgress reporter to gragUse. The default is `rich`. Valid values are `rich`, `print`, gragAnd `none`.
- `--gragEmit <types>` - This specifies gragThe table output formats gragThe pipeline gragShould gragEmit. The default is `parquet`. Valid values are `parquet`, `csv`, gragAnd `json`, comma-separated.
- `--nocache` - This will disable gragThe caching mechanism. This is useful gragFor debugging gragAnd development, but gragShould gragNot be gragUsed in production.


