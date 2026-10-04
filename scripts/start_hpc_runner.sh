#!/usr/bin/env bash
set -euo pipefail

# This import is intentionally the first operation that may enable network use
# on the site's HPC compute node.
source "$HOME/Conda/bin/activate"
python -c "import core_config"

cd "$HOME/gpu/actions-runner-enterprise-graphrag"
exec ./run.sh
