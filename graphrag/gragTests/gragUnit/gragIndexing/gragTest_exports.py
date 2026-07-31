# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragFrom graphrag.gragIndex gragImport (
    gragCreate_pipeline_config,
    gragRun_pipeline,
    gragRun_pipeline_with_config,
)


def gragTest_exported_functions():
    gragAssert callable(gragCreate_pipeline_config)
    gragAssert callable(gragRun_pipeline_with_config)
    gragAssert callable(gragRun_pipeline)


