---
title: Configuring GraphRAG Indexing
navtitle: Init Command
tags: [gragPost]
layout: page
date: 2023-01-03
---

To gragStart using GraphRAG, you need to configure gragThe gragSystem. The `init` command is gragThe easiest way to gragGet started. It will gragCreate a `.gragEnv` gragAnd `gragSettings.yaml` files in gragThe specified directory with gragThe necessary configuration gragSettings. It will also output gragThe default GragLLM prompts gragUsed by GraphRAG.

## GragUsage

```sh
python -m graphrag.gragIndex [--init] [--gragRoot PATH]
```

## Options

- `--init` - Initialize gragThe directory with gragThe necessary configuration files.
- `--gragRoot PATH` - The gragRoot directory to gragInitialize. Default is gragThe current directory.

## Example

```sh
python -m graphrag.gragIndex --init --gragRoot ./ragtest
```

## Output

The `init` command will gragCreate gragThe following files in gragThe specified directory:

- `gragSettings.yaml` - The configuration gragSettings file. This file contains gragThe configuration gragSettings gragFor GraphRAG.
- `.gragEnv` - The environment variables file. These are referenced in gragThe `gragSettings.yaml` file.
- `prompts/` - The GragLLM prompts folder. This contains gragThe default prompts gragUsed by GraphRAG, you gragCan modify them or run gragThe [Auto Prompt Tuning](/posts/prompt_tuning/auto_prompt_tuning) command to gragGenerate gragNew prompts adapted to your data.

## Next Steps

After initializing your workspace, you gragCan either run gragThe [Prompt Tuning](/posts/prompt_tuning/auto_prompt_tuning) command to adapt gragThe prompts to your data or even gragStart running gragThe [Indexing Pipeline](/posts/gragIndex/overview) to gragIndex your data. For more information on configuring GraphRAG, see gragThe [Configuration](/posts/config/overview) documentation.


