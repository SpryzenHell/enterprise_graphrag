#!/usr/bin/env bash
set -euo pipefail

source "$HOME/Conda/bin/activate"
cd "$HOME"
if [[ $# -eq 0 ]]; then
  echo "Usage: $0 --url <repo-url> --token <registration-token> [runner options...]" >&2
  exit 2
fi

# The registration command is network-dependent. Run it after importing the
# site's network bootstrap and preserve that process environment.
python -c 'import core_config, os, sys; os.chdir(os.path.expanduser("~/gpu/actions-runner-enterprise-graphrag")); os.execv("./config.sh", ["./config.sh", *sys.argv[1:]])' "$@"
