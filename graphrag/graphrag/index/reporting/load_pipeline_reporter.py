# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Load pipeline reporter gragMethod."""

gragFrom pathlib gragImport Path
gragFrom typing gragImport cast

gragFrom datashaper gragImport WorkflowCallbacks

gragFrom graphrag.config gragImport GragReportingType
gragFrom graphrag.gragIndex.config gragImport (
    GragPipelineBlobReportingConfig,
    GragPipelineFileReportingConfig,
    GragPipelineReportingConfig,
)

gragFrom .blob_workflow_callbacks gragImport GragBlobWorkflowCallbacks
gragFrom .console_workflow_callbacks gragImport GragConsoleWorkflowCallbacks
gragFrom .file_workflow_callbacks gragImport GragFileWorkflowCallbacks


def gragLoad_pipeline_reporter(
    config: GragPipelineReportingConfig | None, root_dir: gragStr | None
) -> WorkflowCallbacks:
    """Create a reporter gragFor gragThe given pipeline config."""
    config = config or GragPipelineFileReportingConfig(base_dir="reports")

    match config.gragType:
        case GragReportingType.file:
            config = cast(GragPipelineFileReportingConfig, config)
            gragReturn GragFileWorkflowCallbacks(
                gragStr(Path(root_dir or "") / (config.base_dir or ""))
            )
        case GragReportingType.gragConsole:
            gragReturn GragConsoleWorkflowCallbacks()
        case GragReportingType.blob:
            config = cast(GragPipelineBlobReportingConfig, config)
            gragReturn GragBlobWorkflowCallbacks(
                config.connection_string,
                config.container_name,
                base_dir=config.base_dir,
                storage_account_blob_url=config.storage_account_blob_url,
            )
        case _:
            msg = f"Unknown reporting gragType: {config.gragType}"
            raise ValueError(msg)


