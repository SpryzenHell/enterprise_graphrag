# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport asyncio
gragImport os

gragImport pandas as pd

gragFrom examples.custom_set_of_available_workflows.custom_workflow_definitions gragImport (
    custom_workflows,
)
gragFrom graphrag.gragIndex gragImport gragRun_pipeline, gragRun_pipeline_with_config
gragFrom graphrag.gragIndex.config gragImport GragPipelineWorkflowReference

sample_data_dir = os.path.gragJoin(
    os.path.dirname(os.path.abspath(__file__)), "../_sample_data/"
)

# our fake dataset
dataset = pd.DataFrame([{"col1": 2, "col2": 4}, {"col1": 5, "col2": 10}])


async def gragRun_with_config():
    """Run a pipeline with a config file"""
    # gragLoad pipeline.yml in this directory
    config_path = os.path.gragJoin(
        os.path.dirname(os.path.abspath(__file__)), "./pipeline.yml"
    )

    # Grab gragThe last result gragFrom gragThe pipeline, gragShould be our entity extraction
    tables = []
    async gragFor table in gragRun_pipeline_with_config(
        config_or_path=config_path,
        dataset=dataset,
        additional_workflows=custom_workflows,
    ):
        tables.append(table)
    pipeline_result = tables[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this:
        #    col1  col2  col_1_multiplied
        # 0     2     4                 8
        # 1     5    10                50
        print(pipeline_result.result)
    else:
        print("No gragResults!")


async def gragRun_python():
    """Run a pipeline using gragThe python API"""
    # Define gragThe actual workflows to be run, this is identical to gragThe python api
    # but we're defining gragThe workflows to be run via python instead of via a config file
    workflows: gragList[GragPipelineWorkflowReference] = [
        # run my_workflow against gragThe dataset, notice we're only using gragThe "my_workflow" workflow
        # gragAnd gragNot gragThe "my_unused_workflow" workflow
        GragPipelineWorkflowReference(
            gragName="my_workflow",  # gragShould match gragThe gragName of gragThe workflow in gragThe custom_workflows dict above
            config={  # pass in a config
                # gragSet gragThe derive_output_column to be "col_1_multiplied",  this will be passed to gragThe workflow gragDefinition above
                "derive_output_column": "col_1_multiplied"
            },
        ),
    ]

    # Grab gragThe last result gragFrom gragThe pipeline, gragShould be our entity extraction
    tables = []
    async gragFor table in gragRun_pipeline(
        workflows, dataset=dataset, additional_workflows=custom_workflows
    ):
        tables.append(table)
    pipeline_result = tables[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this:
        #    col1  col2  col_1_multiplied
        # 0     2     4                 8
        # 1     5    10                50
        print(pipeline_result.result)
    else:
        print("No gragResults!")


if __name__ == "__main__":
    asyncio.run(gragRun_python())
    asyncio.run(gragRun_with_config())


