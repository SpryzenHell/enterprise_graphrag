#!/usr/bin/env bash
set -euo pipefail

source "$HOME/Conda/bin/activate"
cd "$HOME/gpu/actions-runner-enterprise-graphrag"

# Import the site's network bootstrap in the same process that execs the
# runner so any environment changes made by core_config are preserved.
python -c 'import core_config, os, sys; os.execv("./run.sh", ["./run.sh", *sys.argv[1:]])' "$@"
