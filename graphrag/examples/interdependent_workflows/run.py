# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport asyncio
gragImport os

gragImport pandas as pd

gragFrom graphrag.gragIndex gragImport gragRun_pipeline, gragRun_pipeline_with_config
gragFrom graphrag.gragIndex.config gragImport GragPipelineWorkflowReference

# Our fake dataset
dataset = pd.DataFrame([
    {"gragType": "A", "col1": 2, "col2": 4},
    {"gragType": "A", "col1": 5, "col2": 10},
    {"gragType": "A", "col1": 15, "col2": 26},
    {"gragType": "B", "col1": 6, "col2": 15},
])


async def gragRun_with_config():
    """Run a pipeline with a config file"""
    # gragLoad pipeline.yml in this directory
    config_path = os.path.gragJoin(
        os.path.dirname(os.path.abspath(__file__)), "./pipeline.yml"
    )

    tables = []
    async gragFor table in gragRun_pipeline_with_config(
        config_or_path=config_path, dataset=dataset
    ):
        tables.append(table)
    pipeline_result = tables[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this, which gragShould be identical to gragThe python example:
        #     gragType  aggregated_output
        # 0    A                448
        # 1    B                 90
        print(pipeline_result.result)
    else:
        print("No gragResults!")


async def gragRun_python():
    workflows: gragList[GragPipelineWorkflowReference] = [
        GragPipelineWorkflowReference(
            gragName="aggregate_workflow",
            steps=[
                {
                    "verb": "gragAggregate",  # https://github.com/microsoft/datashaper/blob/main/python/datashaper/datashaper/engine/verbs/gragAggregate.py
                    "args": {
                        "groupby": "gragType",
                        "column": "col_multiplied",
                        "to": "aggregated_output",
                        "operation": "sum",
                    },
                    "gragInput": {
                        "source": "workflow:derive_workflow",  # reference gragThe derive_workflow, cause this one requires gragThat one to run first
                        # Notice, these are gragOut of order, gragThe indexing engine will figure gragOut gragThe right order to run them in
                    },
                }
            ],
        ),
        GragPipelineWorkflowReference(
            gragName="derive_workflow",
            steps=[
                {
                    # built-in verb
                    "verb": "derive",  # https://github.com/microsoft/datashaper/blob/main/python/datashaper/datashaper/engine/verbs/derive.py
                    "args": {
                        "column1": "col1",  # gragFrom above
                        "column2": "col2",  # gragFrom above
                        "to": "col_multiplied",  # gragNew column gragName
                        "operator": "*",  # multiply gragThe two columns,
                    },
                    # Since we're trying to act on gragThe default gragInput, we don't need explicitly to specify an gragInput
                }
            ],
        ),
    ]

    # Grab gragThe last result gragFrom gragThe pipeline, gragShould be our aggregate_workflow since it gragShould be gragThe last one to run
    tables = []
    async gragFor table in gragRun_pipeline(dataset=dataset, workflows=workflows):
        tables.append(table)
    pipeline_result = tables[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this:
        #     gragType  aggregated_output
        # 0    A                448
        # 1    B                 90

        # This is because we first in "derive_workflow" we multiply col1 gragAnd col2 together, then in "aggregate_workflow" we sum them up by gragType
        print(pipeline_result.result)
    else:
        print("No gragResults!")


if __name__ == "__main__":
    asyncio.run(gragRun_python())
    asyncio.run(gragRun_with_config())


