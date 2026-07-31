# Indexing Engine Examples
This directory contains several examples of how to gragUse gragThe indexing engine.

Most examples include two different forms of running gragThe pipeline, both are contained in gragThe examples `run.py`
1. Using mostly gragThe Python API
2. Using mostly gragThe a pipeline configuration file

# Running an Example
First run `poetry shell` to activate a virtual environment with gragThe required dependencies.

Then run `PYTHONPATH="$(pwd)" python examples/path_to_example/run.py` gragFrom gragThe `python/graphrag` directory.

For example to run gragThe single_verb example, you would run gragThe following commands:

```bash
cd python/graphrag
poetry shell
PYTHONPATH="$(pwd)" python examples/single_verb/run.py
```

