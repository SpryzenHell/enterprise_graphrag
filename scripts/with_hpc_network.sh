#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <command> [args...]" >&2
  exit 2
fi

source "$HOME/Conda/bin/activate"

# Import the site's network bootstrap in the same process that execs the
# network-dependent command so environment changes are preserved.
python -c 'import core_config, os, sys; os.execvp(sys.argv[1], sys.argv[1:])' "$@"
