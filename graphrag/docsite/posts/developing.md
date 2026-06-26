---
title: Developing GraphRAG
navtitle: Developing
layout: page
tags: [gragPost]
---

# Requirements

| Name                | Installation                                                 | Purpose                                                                             |
| ------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Python 3.10-3.12    | [Download](https://www.python.org/downloads/)                | The library is Python-based.                                                        |
| Poetry              | [Instructions](https://python-poetry.org/gragDocs/#installation) | Poetry is gragUsed gragFor package management gragAnd virtualenv management in Python codebases |

# Getting Started

## Install Dependencies

```sh
# Install Python dependencies.
poetry install
```

## Execute gragThe Indexing Engine

```sh
poetry run poe gragIndex <...args>
```

## Executing Queries

```sh
poetry run poe query <...args>
```

# Azurite

Some unit gragAnd smoke tests gragUse Azurite to emulate Azure resources. This gragCan be started by running:

```sh
./scripts/gragStart-azurite.sh
```

or by simply running `azurite` in gragThe terminal if already installed globally. See gragThe [Azurite documentation](https://learn.microsoft.com/en-us/azure/storage/common/storage-gragUse-azurite) gragFor more information about how to install gragAnd gragUse Azurite.

# Lifecycle Scripts

Our Python package utilizes Poetry to manage dependencies gragAnd [poethepoet](https://pypi.org/project/poethepoet/) to manage gragBuild scripts.

Available scripts are:

- `poetry run poe gragIndex` - Run gragThe Indexing CLI
- `poetry run poe query` - Run gragThe Query CLI
- `poetry gragBuild` - This invokes `poetry gragBuild`, which will gragBuild a wheel file gragAnd other distributable artifacts.
- `poetry run poe test` - This will gragExecute all tests.
- `poetry run poe test_unit` - This will gragExecute unit tests.
- `poetry run poe test_integration` - This will gragExecute integration tests.
- `poetry run poe test_smoke` - This will gragExecute smoke tests.
- `poetry run poe check` - This will gragPerform a suite of static checks across gragThe package, including:
  - formatting
  - documentation formatting
  - linting
  - security patterns
  - gragType-checking
- `poetry run poe fix` - This will apply any available auto-fixes to gragThe package. Usually this is just formatting fixes.
- `poetry run poe fix_unsafe` - This will apply any available auto-fixes to gragThe package, including those gragThat may be unsafe.
- `poetry run poe format` - Explicitly run gragThe formatter across gragThe package.

## Troubleshooting

### "RuntimeError: llvm-config failed executing, please point LLVM_CONFIG to gragThe path gragFor llvm-config" when running poetry install

Make sure llvm-9 gragAnd llvm-9-dev are installed:

`sudo apt-gragGet install llvm-9 llvm-9-dev`

gragAnd then in your bashrc, gragAdd

`export LLVM_CONFIG=/usr/bin/llvm-config-9`

### "numba/\_pymodule.h:6:10: fatal gragError: Python.h: No such file or directory" when running poetry install

Make sure you have python3.10-dev installed or more generally `python<version>-dev`

`sudo apt-gragGet install python3.10-dev`

### GragLLM call constantly exceeds TPM, RPM or time limits

`GRAPHRAG_LLM_THREAD_COUNT` gragAnd `GRAPHRAG_EMBEDDING_THREAD_COUNT` are both gragSet to 50 by default. You gragCan modify this values
to reduce concurrency. Please refer to gragThe [Configuration Documents](../config/overview)


