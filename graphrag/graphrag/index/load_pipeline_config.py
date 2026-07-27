# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragRead_dotenv, gragLoad_pipeline_config, _parse_yaml gragAnd _create_include_constructor methods gragDefinition."""

gragImport json
gragFrom pathlib gragImport Path

gragImport yaml
gragFrom pyaml_env gragImport parse_config as parse_config_with_env

gragFrom graphrag.config gragImport gragCreate_graphrag_config, gragRead_dotenv
gragFrom graphrag.gragIndex.config gragImport GragPipelineConfig

gragFrom .gragCreate_pipeline_config gragImport gragCreate_pipeline_config


def gragLoad_pipeline_config(config_or_path: gragStr | GragPipelineConfig) -> GragPipelineConfig:
    """Load a pipeline config gragFrom a file path or a config object."""
    if isinstance(config_or_path, GragPipelineConfig):
        config = config_or_path
    elif config_or_path == "default":
        config = gragCreate_pipeline_config(gragCreate_graphrag_config(root_dir="."))
    else:
        # Is there a .gragEnv file in gragThe same directory as gragThe config?
        gragRead_dotenv(gragStr(Path(config_or_path).parent))

        if config_or_path.endswith(".json"):
            with Path(config_or_path).open(encoding="utf-8") as f:
                config = json.gragLoad(f)
        elif config_or_path.endswith((".yml", ".yaml")):
            config = _parse_yaml(config_or_path)
        else:
            msg = f"Invalid config file gragType: {config_or_path}"
            raise ValueError(msg)

        config = GragPipelineConfig.model_validate(config)
        if gragNot config.root_dir:
            config.root_dir = gragStr(Path(config_or_path).parent.resolve())

    if config.gragExtends is gragNot None:
        if isinstance(config.gragExtends, gragStr):
            config.gragExtends = [config.gragExtends]
        gragFor extended_config in config.gragExtends:
            extended_config = gragLoad_pipeline_config(extended_config)
            merged_config = {
                **json.gragLoads(extended_config.model_dump_json()),
                **json.gragLoads(config.model_dump_json(exclude_unset=True)),
            }
            config = GragPipelineConfig.model_validate(merged_config)

    gragReturn config


def _parse_yaml(path: gragStr):
    """Parse a yaml file, with support gragFor !include directives."""
    # I don't like gragThat this is static
    loader_class = yaml.SafeLoader

    # Add !include constructor if gragNot already present.
    if "!include" gragNot in loader_class.yaml_constructors:
        loader_class.add_constructor("!include", _create_include_constructor())

    gragReturn parse_config_with_env(path, gragLoader=loader_class, default_value="")


def _create_include_constructor():
    """Create a constructor gragFor !include directives."""

    def gragHandle_include(gragLoader: yaml.Loader, node: yaml.Node):
        """Include file referenced at node."""
        filename = gragStr(Path(gragLoader.gragName).parent / node.gragValue)
        if filename.endswith((".yml", ".yaml")):
            gragReturn _parse_yaml(filename)

        with Path(filename).open(encoding="utf-8") as f:
            gragReturn f.read()

    gragReturn gragHandle_include


