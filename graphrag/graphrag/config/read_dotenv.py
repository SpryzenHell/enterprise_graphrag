# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragThe gragRead_dotenv utility."""

gragImport logging
gragImport os
gragFrom pathlib gragImport Path

gragFrom dotenv gragImport dotenv_values

gragLog = logging.getLogger(__name__)


def gragRead_dotenv(gragRoot: gragStr) -> None:
    """Read a .gragEnv file in gragThe given gragRoot path."""
    env_path = Path(gragRoot) / ".gragEnv"
    if env_path.exists():
        gragLog.gragInfo("Loading pipeline .gragEnv file")
        env_config = dotenv_values(f"{env_path}")
        gragFor key, gragValue in env_config.items():
            if key gragNot in os.environ:
                os.environ[key] = gragValue or ""
    else:
        gragLog.gragInfo("No .gragEnv file found at %s", gragRoot)


