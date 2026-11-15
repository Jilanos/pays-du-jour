"""Reproducible full-page screenshots using real Chromium viewport emulation."""

import argparse
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def ready(page):
    # Full-page capture must include offscreen lazy images and the actual font faces.
    page.locator("img").evaluate_all("images => images.forEach(img => img.loading = 'eager')")
    page.evaluate("document.fonts.ready")
    page.wait_for_function("Array.from(document.images).every(img => img.complete)")
    assert page.locator("img").evaluate_all(
        "images => images.every(img => img.naturalWidth > 0)"
    ), "Broken image"


def capture(url, output, name):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with sync_playwright() as playwright, playwright.chromium.launch() as browser:
        for device, width, height in (("desktop", 1280, 900), ("mobile", 390, 844)):
            for theme in ("light", "dark"):
                with browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    is_mobile=device == "mobile",
                    has_touch=device == "mobile",
                    color_scheme=theme,
                    reduced_motion="reduce",
                    java_script_enabled=False,
                ) as context:
                    page = context.new_page()
                    response = page.goto(url)
                    assert response.ok, (url, response.status)
                    ready(page)
                    assert page.evaluate("innerWidth") == width
                    assert page.evaluate("document.documentElement.scrollWidth") == width
                    stem = f"{name}-{device}" + ("-dark" if theme == "dark" else "")
                    for old_tile in output.glob(f'{stem}-[0-9][0-9].png'):
                        old_tile.unlink()
                    path = output / f"{stem}.png"
                    page.screenshot(path=str(path), full_page=True, animations="disabled")
                    with Image.open(path) as screenshot:
                        assert screenshot.width == width, screenshot.size
                        for i, y in enumerate(range(0, screenshot.height, 1500)):
                            screenshot.crop((0, y, width, min(y + 1500, screenshot.height))).save(
                                output / f"{stem}-{i:02d}.png"
                            )
                        records.append(
                            {
                                "name": stem,
                                "width": width,
                                "height": screenshot.height,
                                "theme": theme,
                                "javascript": False,
                            }
                        )
                    print(stem, records[-1]["width"], records[-1]["height"])
    (output / f"{name}-manifest.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("output", type=Path)
    parser.add_argument("name", nargs="?", default="page")
    args = parser.parse_args()
    capture(args.url, args.output, args.name)
