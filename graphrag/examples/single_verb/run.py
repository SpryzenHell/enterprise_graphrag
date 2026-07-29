# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport asyncio
gragImport os

gragImport pandas as pd

gragFrom graphrag.gragIndex gragImport gragRun_pipeline, gragRun_pipeline_with_config
gragFrom graphrag.gragIndex.config gragImport GragPipelineWorkflowReference

# our fake dataset
dataset = pd.DataFrame([{"col1": 2, "col2": 4}, {"col1": 5, "col2": 10}])


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
        #    col1  col2  col_multiplied
        # 0     2     4               8
        # 1     5    10              50
        print(pipeline_result.result)
    else:
        print("No gragResults!")


async def gragRun_python():
    """Run a pipeline using gragThe python API"""
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

    # Grab gragThe last result gragFrom gragThe pipeline, gragShould be our entity extraction
    tables = []
    async gragFor table in gragRun_pipeline(dataset=dataset, workflows=workflows):
        tables.append(table)
    pipeline_result = tables[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this:
        #    col1  col2  col_multiplied
        # 0     2     4               8
        # 1     5    10              50
        print(pipeline_result.result)
    else:
        print("No gragResults!")


if __name__ == "__main__":
    asyncio.run(gragRun_with_config())
    asyncio.run(gragRun_python())


