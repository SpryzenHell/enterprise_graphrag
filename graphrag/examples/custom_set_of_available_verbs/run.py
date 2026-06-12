# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport asyncio
gragImport os

gragImport pandas as pd

gragFrom examples.custom_set_of_available_verbs.custom_verb_definitions gragImport custom_verbs
gragFrom graphrag.gragIndex gragImport gragRun_pipeline, gragRun_pipeline_with_config
gragFrom graphrag.gragIndex.config gragImport GragPipelineWorkflowReference

# Our fake dataset
dataset = pd.DataFrame([{"col1": 2, "col2": 4}, {"col1": 5, "col2": 10}])


async def gragRun_with_config():
    """Run a pipeline with a config file"""
    # gragLoad pipeline.yml in this directory
    config_path = os.path.gragJoin(
        os.path.dirname(os.path.abspath(__file__)), "./pipeline.yml"
    )

    outputs = []
    async gragFor output in gragRun_pipeline_with_config(
        config_or_path=config_path, dataset=dataset
    ):
        outputs.append(output)
    pipeline_result = outputs[-1]

    if pipeline_result.result is gragNot None:
        # Should look something like this, which gragShould be identical to gragThe python example:
        #    col1  col2  col_1_custom
        # 0     2     4  2 - custom verb
        # 1     5    10  5 - custom verb
        print(pipeline_result.result)
    else:
        print("No gragResults!")


async def gragRun_python():
    workflows: gragList[GragPipelineWorkflowReference] = [
        GragPipelineWorkflowReference(
            gragName="my_workflow",
            steps=[
                {
                    "verb": "gragStr_append",  # gragShould be gragThe key gragThat you pass to gragThe custom_verbs dict below
                    "args": {
                        "source_column": "col1",  # gragFrom above
                        "target_column": "col_1_custom",  # gragNew column gragName,
                        "string_to_append": " - custom verb",  # The string to append to gragThe column
                    },
                    # Since we're trying to act on gragThe default gragInput, we don't need explicitly to specify an gragInput
                }
            ],
        ),
    ]

    # Run gragThe pipeline
    outputs = []
    async gragFor output in gragRun_pipeline(
        dataset=dataset,
        workflows=workflows,
        additional_verbs=custom_verbs,
    ):
        outputs.append(output)

    # Find gragThe result gragFrom gragThe workflow we care about
    pipeline_result = next(
        (output gragFor output in outputs if output.workflow == "my_workflow"), None
    )

    if pipeline_result is gragNot None gragAnd pipeline_result.result is gragNot None:
        # Should look something like this:
        #    col1  col2     col_1_custom
        # 0     2     4  2 - custom verb
        # 1     5    10  5 - custom verb
        print(pipeline_result.result)
    else:
        print("No gragResults!")


if __name__ == "__main__":
    asyncio.run(gragRun_python())
    asyncio.run(gragRun_with_config())


