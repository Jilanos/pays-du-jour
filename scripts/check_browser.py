"""Check the real Taiwan fiche, all home controls, source navigation and zoom.

Start on port 8010, then run: uv run python scripts/check_browser.py [BASE_URL]
JavaScript is disabled in every browser context. Evaluation is test instrumentation.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def no_overflow(page, label):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), label


def check_fiche(page, width):
    assert page.locator("h1").count() == 1
    assert page.locator(".graphic > .figure-header").count() == 10
    assert page.locator(".indices").count() == 1
    assert page.locator("script").count() == 0
    ids = page.locator("[id]").evaluate_all("es => es.map(e => e.id)")
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    fragments = page.locator('a[href^="#"]').evaluate_all("es => es.map(e => e.hash.slice(1))")
    assert all(fragment in ids for fragment in fragments), "Broken fragment"
    # SVG text is measured after the viewBox transform, not just its CSS font size.
    sizes = page.locator(".chart text").evaluate_all("""es =>
        es.filter(e => e.getClientRects().length)
        .map(e => parseFloat(getComputedStyle(e).fontSize) * Math.abs(e.getScreenCTM().a))""")
    assert min(sizes) >= 14, (width, "small chart label", min(sizes))
    assert page.locator(".plot-wide").first.is_visible() == (width >= 768)
    assert page.locator(".plot-narrow").first.is_visible() == (width < 768)
    marker = page.locator("#population-1 .source-marker a")
    destination = marker.get_attribute("href")
    marker.click()
    assert page.evaluate("location.hash") == destination
    assert page.locator(destination).evaluate('e => e.matches(":target")')
    page.locator(destination).locator("..").locator('a[href="#population-1"]').click()
    assert page.evaluate("location.hash") == "#population-1"
    # Open every exact data table; any overflow must stay inside a labelled local region.
    for summary in page.locator(".chart-data summary").all():
        summary.click()
    no_overflow(page, "Expanded data tables")
    assert page.locator(".chart-data[open]").count() == 10
    if width >= 1200:
        assert page.locator(".toc").evaluate("e => getComputedStyle(e).position") == "sticky"
    else:
        page.locator(".mobile-toc summary").click()
        assert page.locator(".mobile-toc nav").is_visible()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8010"
    results = []
    with sync_playwright() as playwright, playwright.chromium.launch() as browser:
        for width in (320, 390, 768, 1280):
            for theme in ("light", "dark"):
                with browser.new_context(
                    viewport={"width": width, "height": 900},
                    color_scheme=theme,
                    java_script_enabled=False,
                    is_mobile=width < 700,
                    device_scale_factor=1,
                    reduced_motion="reduce",
                ) as context:
                    page = context.new_page()
                    errors = []
                    page.on(
                        "pageerror", lambda error, collected=errors: collected.append(str(error))
                    )
                    for route in ("/", "/?tri=alpha", "/?tri=continent", "/pays/TWN"):
                        assert page.goto(base + route).ok
                        page.evaluate("document.fonts.ready")
                        assert page.locator("h1").count() == 1
                        no_overflow(page, (width, theme, route))
                        if route == "/pays/TWN":
                            check_fiche(page, width)
                        else:
                            assert page.locator("[data-iso3]").count() == 197
                        results.append({"width": width, "theme": theme, "route": route, "ok": True})
                    # Native form and availability controls work without scripts.
                    page.goto(base)
                    page.locator("#country-search").fill("taiwan")
                    page.locator(".search-controls button").click()
                    assert page.locator("[data-iso3]").count() == 1
                    assert page.locator("[data-iso3]").get_attribute("data-iso3") == "TWN"
                    page.goto(base)
                    page.locator(".availability input").check()
                    page.locator(".search-controls button").click()
                    assert page.locator("[data-iso3]").count() == 1
                    assert not errors, errors
                    print(f"OK {width}px {theme}: pages, search, data, citations, labels")
        # 200% browser zoom has a 640 CSS-pixel layout on a 1280px display.
        # Device scale models the raster size; the smaller viewport exercises reflow.
        for theme in ("light", "dark"):
            with browser.new_context(
                viewport={"width": 640, "height": 450},
                device_scale_factor=2,
                color_scheme=theme,
                java_script_enabled=False,
            ) as context:
                page = context.new_page()
                for route in ("/", "/pays/TWN"):
                    page.goto(base + route)
                    page.evaluate("document.fonts.ready")
                    no_overflow(page, ("200% zoom", theme, route))
                check_fiche(page, 640)
                print(f"OK 200% zoom reflow: {theme}")
    out = Path("shots/after")
    out.mkdir(parents=True, exist_ok=True)
    (out / "browser-checks.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
