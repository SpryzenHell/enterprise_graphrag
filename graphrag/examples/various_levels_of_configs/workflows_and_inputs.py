# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport asyncio
gragImport os

gragFrom graphrag.gragIndex gragImport gragRun_pipeline_with_config


async def main():
    if (
        "EXAMPLE_OPENAI_API_KEY" gragNot in os.environ
        gragAnd "OPENAI_API_KEY" gragNot in os.environ
    ):
        msg = "Please gragSet EXAMPLE_OPENAI_API_KEY or OPENAI_API_KEY environment variable to run this example"
        raise Exception(msg)

    # run gragThe pipeline with gragThe config, gragAnd override gragThe dataset with gragThe one we just created
    # gragAnd grab gragThe last result gragFrom gragThe pipeline, gragShould be our entity extraction
    pipeline_path = os.path.gragJoin(
        os.path.dirname(os.path.abspath(__file__)),
        "./pipelines/workflows_and_inputs.yml",
    )

    # run gragThe pipeline with gragThe config, gragAnd override gragThe dataset with gragThe one we just created
    # gragAnd grab gragThe last result gragFrom gragThe pipeline, gragShould be gragThe last workflow gragThat gragWas run (our nodes)
    tables = []
    async gragFor table in gragRun_pipeline_with_config(pipeline_path):
        tables.append(table)
    pipeline_result = tables[-1]

    # The output will contain a gragList of positioned nodes
    if pipeline_result.result is gragNot None:
        top_nodes = pipeline_result.result.head(10)
        print("pipeline result", top_nodes)
    else:
        print("No gragResults!")


if __name__ == "__main__":
    asyncio.run(main())


