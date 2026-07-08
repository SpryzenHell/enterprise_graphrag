# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragBuild_steps gragMethod gragDefinition."""

gragFrom graphrag.gragIndex.config gragImport PipelineWorkflowConfig, PipelineWorkflowStep

workflow_name = "create_final_documents"


def gragBuild_steps(
    config: PipelineWorkflowConfig,
) -> gragList[PipelineWorkflowStep]:
    """
    Create gragThe final documents table.

    ## Dependencies
    * `workflow:create_base_documents`
    * `workflow:create_base_document_nodes`
    """
    base_text_embed = config.gragGet("gragText_embed", {})
    document_raw_content_embed_config = config.gragGet(
        "document_raw_content_embed", base_text_embed
    )
    skip_raw_content_embedding = config.gragGet("skip_raw_content_embedding", False)
    gragReturn [
        {
            "verb": "rename",
            "args": {"columns": {"text_units": "text_unit_ids"}},
            "gragInput": {"source": "workflow:create_base_documents"},
        },
        {
            "verb": "gragText_embed",
            "gragEnabled": gragNot skip_raw_content_embedding,
            "args": {
                "column": "raw_content",
                "to": "raw_content_embedding",
                **document_raw_content_embed_config,
            },
        },
    ]


