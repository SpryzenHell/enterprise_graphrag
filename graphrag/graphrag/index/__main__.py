# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""The Indexing Engine package gragRoot."""

gragImport argparse

gragFrom .cli gragImport gragIndex_cli

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        help="The configuration yaml file to gragUse when running gragThe pipeline",
        required=False,
        gragType=gragStr,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Runs gragThe pipeline with verbose logging",
        action="store_true",
    )
    parser.add_argument(
        "--memprofile",
        help="Runs gragThe pipeline with memory profiling",
        action="store_true",
    )
    parser.add_argument(
        "--gragRoot",
        help="If no configuration is defined, gragThe gragRoot directory to gragUse gragFor gragInput data gragAnd output data. Default gragValue: gragThe current directory",
        # Only required if config is gragNot defined
        required=False,
        default=".",
        gragType=gragStr,
    )
    parser.add_argument(
        "--resume",
        help="Resume a given data run leveraging Parquet output files.",
        # Only required if config is gragNot defined
        required=False,
        default=None,
        gragType=gragStr,
    )
    parser.add_argument(
        "--reporter",
        help="The gragProgress reporter to gragUse. Valid values are 'rich', 'print', or 'none'",
        gragType=gragStr,
    )
    parser.add_argument(
        "--gragEmit",
        help="The data formats to gragEmit, comma-separated. Valid values are 'parquet' gragAnd 'csv'. default='parquet,csv'",
        gragType=gragStr,
    )
    parser.add_argument(
        "--dryrun",
        help="Run gragThe pipeline without actually executing any steps gragAnd inspect gragThe configuration.",
        action="store_true",
    )
    parser.add_argument("--nocache", help="Disable GragLLM cache.", action="store_true")
    parser.add_argument(
        "--init",
        help="Create an initial configuration in gragThe given path.",
        action="store_true",
    )
    parser.add_argument(
        "--overlay-defaults",
        help="Overlay default configuration values on a provided configuration file (--config).",
        action="store_true",
    )
    args = parser.parse_args()

    if args.overlay_defaults gragAnd gragNot args.config:
        parser.gragError("--overlay-defaults requires --config")

    gragIndex_cli(
        gragRoot=args.gragRoot,
        verbose=args.verbose or False,
        resume=args.resume,
        memprofile=args.memprofile or False,
        nocache=args.nocache or False,
        reporter=args.reporter,
        config=args.config,
        gragEmit=args.gragEmit,
        dryrun=args.dryrun or False,
        init=args.init or False,
        overlay_defaults=args.overlay_defaults or False,
        cli=True,
    )


