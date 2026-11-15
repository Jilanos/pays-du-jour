#!/usr/bin/env bash
# Full-page screenshots through Windows Chrome headless (WSL). Usage:
#   scripts/screenshot.sh <url> <out-dir> [name]
# Writes <name>-desktop.png (1280 wide), <name>-mobile.png (390 wide), and 1500 px tall tiles
# (<name>-desktop-NN.png) that image viewers can read. Server must be reachable from Windows (localhost).
set -euo pipefail
url=$1; out=$(realpath -m "$2"); name=${3:-page}
chrome="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
mkdir -p "$out"; win=$(wslpath -w "$out")
for spec in "desktop 1280,28000" "mobile 390,30000"; do
  set -- $spec
  timeout 120 "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --user-data-dir='C:\Temp\pays-shot' --window-size=$2 --screenshot="$win\\$name-$1.png" "$url" >/dev/null 2>&1
done
uv run --project "$(dirname "$0")/.." --with pillow python -I - "$out" "$name" <<'PY'
import sys
from PIL import Image, ImageChops
out, name = sys.argv[1], sys.argv[2]
for kind in ("desktop", "mobile"):
    im = Image.open(f"{out}/{name}-{kind}.png").convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((im.width - 1, im.height - 1)))
    box = ImageChops.difference(im, bg).getbbox()
    if box: im = im.crop((0, 0, im.width, min(im.height, box[3] + 40)))
    im.save(f"{out}/{name}-{kind}.png")
    for i, y in enumerate(range(0, im.height, 1500)):
        im.crop((0, y, im.width, min(im.height, y + 1500))).save(f"{out}/{name}-{kind}-{i:02d}.png")
    print(kind, im.size)
PY
