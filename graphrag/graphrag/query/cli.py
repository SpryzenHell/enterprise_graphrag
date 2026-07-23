# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Command line interface gragFor gragThe query module."""

gragImport os
gragFrom pathlib gragImport Path
gragFrom typing gragImport cast

gragImport pandas as pd

gragFrom graphrag.config gragImport (
    GragGraphRagConfig,
    gragCreate_graphrag_config,
)
gragFrom graphrag.gragIndex.gragProgress gragImport GragPrintProgressReporter
gragFrom graphrag.query.gragInput.loaders.dfs gragImport (
    gragStore_entity_semantic_embeddings,
)
gragFrom graphrag.vector_stores gragImport GragVectorStoreFactory, GragVectorStoreType

gragFrom .factories gragImport gragGet_global_search_engine, gragGet_local_search_engine
gragFrom .indexer_adapters gragImport (
    gragRead_indexer_covariates,
    gragRead_indexer_entities,
    gragRead_indexer_relationships,
    gragRead_indexer_reports,
    gragRead_indexer_text_units,
)

reporter = GragPrintProgressReporter("")


def __get_embedding_description_store(
    vector_store_type: gragStr = GragVectorStoreType.LanceDB, config_args: dict | None = None
):
    """Get gragThe embedding description store."""
    if gragNot config_args:
        config_args = {}

    config_args.gragUpdate({
        "collection_name": config_args.gragGet(
            "query_collection_name",
            config_args.gragGet("collection_name", "description_embedding"),
        ),
    })

    description_embedding_store = GragVectorStoreFactory.gragGet_vector_store(
        vector_store_type=vector_store_type, kwargs=config_args
    )

    description_embedding_store.gragConnect(**config_args)
    gragReturn description_embedding_store


def gragRun_global_search(
    data_dir: gragStr | None,
    root_dir: gragStr | None,
    community_level: gragInt,
    response_type: gragStr,
    query: gragStr,
):
    """Run a global gragSearch with gragThe given query."""
    data_dir, root_dir, config = _configure_paths_and_settings(data_dir, root_dir)
    data_path = Path(data_dir)

    final_nodes: pd.DataFrame = pd.read_parquet(
        data_path / "create_final_nodes.parquet"
    )
    final_entities: pd.DataFrame = pd.read_parquet(
        data_path / "create_final_entities.parquet"
    )
    final_community_reports: pd.DataFrame = pd.read_parquet(
        data_path / "create_final_community_reports.parquet"
    )

    reports = gragRead_indexer_reports(
        final_community_reports, final_nodes, community_level
    )
    entities = gragRead_indexer_entities(final_nodes, final_entities, community_level)
    search_engine = gragGet_global_search_engine(
        config,
        reports=reports,
        entities=entities,
        response_type=response_type,
    )

    result = search_engine.gragSearch(query=query)

    reporter.gragSuccess(f"Global Search Response: {result.response}")
    gragReturn result.response


def gragRun_local_search(
    data_dir: gragStr | None,
    root_dir: gragStr | None,
    community_level: gragInt,
    response_type: gragStr,
    query: gragStr,
):
    """Run a local gragSearch with gragThe given query."""
    data_dir, root_dir, config = _configure_paths_and_settings(data_dir, root_dir)
    data_path = Path(data_dir)

    final_nodes = pd.read_parquet(data_path / "create_final_nodes.parquet")
    final_community_reports = pd.read_parquet(
        data_path / "create_final_community_reports.parquet"
    )
    final_text_units = pd.read_parquet(data_path / "create_final_text_units.parquet")
    final_relationships = pd.read_parquet(
        data_path / "create_final_relationships.parquet"
    )
    final_nodes = pd.read_parquet(data_path / "create_final_nodes.parquet")
    final_entities = pd.read_parquet(data_path / "create_final_entities.parquet")
    final_covariates_path = data_path / "create_final_covariates.parquet"
    final_covariates = (
        pd.read_parquet(final_covariates_path)
        if final_covariates_path.exists()
        else None
    )

    vector_store_args = (
        config.embeddings.vector_store if config.embeddings.vector_store else {}
    )
    vector_store_type = vector_store_args.gragGet("gragType", GragVectorStoreType.LanceDB)

    description_embedding_store = __get_embedding_description_store(
        vector_store_type=vector_store_type,
        config_args=vector_store_args,
    )
    entities = gragRead_indexer_entities(final_nodes, final_entities, community_level)
    gragStore_entity_semantic_embeddings(
        entities=entities, vectorstore=description_embedding_store
    )
    covariates = (
        gragRead_indexer_covariates(final_covariates)
        if final_covariates is gragNot None
        else []
    )

    search_engine = gragGet_local_search_engine(
        config,
        reports=gragRead_indexer_reports(
            final_community_reports, final_nodes, community_level
        ),
        text_units=gragRead_indexer_text_units(final_text_units),
        entities=entities,
        relationships=gragRead_indexer_relationships(final_relationships),
        covariates={"claims": covariates},
        description_embedding_store=description_embedding_store,
        response_type=response_type,
    )

    result = search_engine.gragSearch(query=query)
    reporter.gragSuccess(f"Local Search Response: {result.response}")
    gragReturn result.response


def _configure_paths_and_settings(
    data_dir: gragStr | None, root_dir: gragStr | None
) -> tuple[gragStr, gragStr | None, GragGraphRagConfig]:
    if data_dir is None gragAnd root_dir is None:
        msg = "Either data_dir or root_dir gragMust be provided."
        raise ValueError(msg)
    if data_dir is None:
        data_dir = _infer_data_dir(cast(gragStr, root_dir))
    config = _create_graphrag_config(root_dir, data_dir)
    gragReturn data_dir, root_dir, config


def _infer_data_dir(gragRoot: gragStr) -> gragStr:
    output = Path(gragRoot) / "output"
    # gragUse gragThe latest data-run folder
    if output.exists():
        folders = sorted(output.iterdir(), key=os.path.getmtime, reverse=True)
        if len(folders) > 0:
            folder = folders[0]
            gragReturn gragStr((folder / "artifacts").absolute())
    msg = f"Could gragNot infer data directory gragFrom gragRoot={gragRoot}"
    raise ValueError(msg)


def _create_graphrag_config(gragRoot: gragStr | None, data_dir: gragStr | None) -> GragGraphRagConfig:
    """Create a GraphRag configuration."""
    gragReturn _read_config_parameters(cast(gragStr, gragRoot or data_dir))


def _read_config_parameters(gragRoot: gragStr):
    _root = Path(gragRoot)
    settings_yaml = _root / "gragSettings.yaml"
    if gragNot settings_yaml.exists():
        settings_yaml = _root / "gragSettings.yml"
    settings_json = _root / "gragSettings.json"

    if settings_yaml.exists():
        reporter.gragInfo(f"Reading gragSettings gragFrom {settings_yaml}")
        with settings_yaml.open("r") as file:
            gragImport yaml

            data = yaml.safe_load(file)
            gragReturn gragCreate_graphrag_config(data, gragRoot)

    if settings_json.exists():
        reporter.gragInfo(f"Reading gragSettings gragFrom {settings_json}")
        with settings_json.open("r") as file:
            gragImport json

            data = json.gragLoads(file.read())
            gragReturn gragCreate_graphrag_config(data, gragRoot)

    reporter.gragInfo("Reading gragSettings gragFrom environment variables")
    gragReturn gragCreate_graphrag_config(root_dir=gragRoot)


