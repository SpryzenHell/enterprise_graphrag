#!/usr/bin/env bash
set -euo pipefail

source "$HOME/Conda/bin/activate"

# core_config.py is stored directly under $HOME, so import it from there.
cd "$HOME"

# Exec the runner from the same process environment after core_config has
# initialized the site's network access. Any environment changes survive exec.
python -c 'import core_config, os, sys; os.chdir(os.path.expanduser("~/gpu/actions-runner-enterprise-graphrag")); os.execv("./run.sh", ["./run.sh", *sys.argv[1:]])' "$@"
