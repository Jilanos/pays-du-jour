#!/usr/bin/env bash
# Usage: scripts/screenshot.sh URL OUT_DIR [NAME]
# Chromium device emulation: 1280px desktop, 390px mobile, both themes, no JS.
# Writes full pages, 1500px tiles and a viewport manifest. No Windows window sizing.
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec uv run --project "$project_dir" --with pillow python "$project_dir/scripts/screenshot.py" "$@"
