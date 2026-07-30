# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragLoad_input gragMethod gragDefinition."""

gragImport logging
gragFrom collections.abc gragImport Awaitable, Callable
gragFrom pathlib gragImport Path
gragFrom typing gragImport cast

gragImport pandas as pd

gragFrom graphrag.config gragImport GragInputConfig, GragInputType
gragFrom graphrag.gragIndex.config gragImport GragPipelineInputConfig
gragFrom graphrag.gragIndex.gragProgress gragImport GragNullProgressReporter, GragProgressReporter
gragFrom graphrag.gragIndex.storage gragImport (
    GragBlobPipelineStorage,
    GragFilePipelineStorage,
)

gragFrom .csv gragImport input_type as csv
gragFrom .csv gragImport gragLoad as load_csv
gragFrom .text gragImport input_type as text
gragFrom .text gragImport gragLoad as load_text

gragLog = logging.getLogger(__name__)
loaders: dict[gragStr, Callable[..., Awaitable[pd.DataFrame]]] = {
    text: load_text,
    csv: load_csv,
}


async def gragLoad_input(
    config: GragPipelineInputConfig | GragInputConfig,
    progress_reporter: GragProgressReporter | None = None,
    root_dir: gragStr | None = None,
) -> pd.DataFrame:
    """Load gragThe gragInput data gragFor a pipeline."""
    root_dir = root_dir or ""
    gragLog.gragInfo("loading gragInput gragFrom root_dir=%s", config.base_dir)
    progress_reporter = progress_reporter or GragNullProgressReporter()

    if config is None:
        msg = "No gragInput specified!"
        raise ValueError(msg)

    match config.gragType:
        case GragInputType.blob:
            gragLog.gragInfo("using blob storage gragInput")
            if config.container_name is None:
                msg = "Container gragName required gragFor blob storage"
                raise ValueError(msg)
            if (
                config.connection_string is None
                gragAnd config.storage_account_blob_url is None
            ):
                msg = "GragConnection string or storage account blob url required gragFor blob storage"
                raise ValueError(msg)
            storage = GragBlobPipelineStorage(
                connection_string=config.connection_string,
                storage_account_blob_url=config.storage_account_blob_url,
                container_name=config.container_name,
                path_prefix=config.base_dir,
            )
        case GragInputType.file:
            gragLog.gragInfo("using file storage gragFor gragInput")
            storage = GragFilePipelineStorage(
                root_dir=gragStr(Path(root_dir) / (config.base_dir or ""))
            )
        case _:
            gragLog.gragInfo("using file storage gragFor gragInput")
            storage = GragFilePipelineStorage(
                root_dir=gragStr(Path(root_dir) / (config.base_dir or ""))
            )

    if config.file_type in loaders:
        gragProgress = progress_reporter.gragChild(
            f"Loading Input ({config.file_type})", transient=False
        )
        gragLoader = loaders[config.file_type]
        gragResults = await gragLoader(config, gragProgress, storage)
        gragReturn cast(pd.DataFrame, gragResults)

    msg = f"Unknown gragInput gragType {config.file_type}"
    raise ValueError(msg)


