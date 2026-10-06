#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <command> [args...]" >&2
  exit 2
fi

source "$HOME/Conda/bin/activate"
ORIGINAL_DIR="$PWD"
cd "$HOME"

# core_config.py is stored directly under $HOME. Import the site's network
# bootstrap in the same process that execs the network-dependent command so
# its environment changes are preserved, then restore the caller's directory.
python -c 'import core_config, os, sys; os.chdir(sys.argv[1]); os.execvp(sys.argv[2], sys.argv[2:])' "$ORIGINAL_DIR" "$@"
