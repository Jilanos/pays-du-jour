"""Check local pages at mobile and desktop sizes, in light and dark, without JS.

Start the fixture server first. Screenshots are written outside the repository.
Run: uv run python scripts/check_browser.py [http://127.0.0.1:8001]
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
    screenshots = Path("/tmp/pays-du-jour-preview")
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        with playwright.chromium.launch(
            executable_path=playwright.chromium.executable_path
        ) as browser:
            for width in (375, 1440):
                for theme in ("light", "dark"):
                    context = browser.new_context(
                        viewport={"width": width, "height": 900},
                        color_scheme=theme,
                        java_script_enabled=False,
                    )
                    page = context.new_page()
                    errors = []
                    page.on(
                        "pageerror", lambda error, collected=errors: collected.append(str(error))
                    )
                    for route, label in (
                        ("/", "home"),
                        ("/?tri=alpha", "alpha"),
                        ("/pays/FRA", "fiche"),
                    ):
                        response = page.goto(base + route)
                        assert response.status == 200, (route, response.status)
                        assert page.locator("h1").count() == 1
                        overflow = page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                        assert not overflow, (width, theme, route, "horizontal overflow")
                        assert page.locator("script").count() == 0
                        if label == "fiche":
                            assert page.locator("svg").count() == 9
                            assert page.get_by_text("{{", exact=False).count() == 0
                            if width > 1200:
                                assert (
                                    page.locator(".toc nav").evaluate(
                                        "e => getComputedStyle(e).position"
                                    )
                                    == "sticky"
                                )
                            # Expanded tables stay inside their own scroll container.
                            for details in page.locator(".graphic details").all():
                                details.locator("summary").click()
                            assert not page.evaluate(
                                "document.documentElement.scrollWidth > innerWidth"
                            )
                        page.screenshot(
                            path=str(screenshots / f"{label}-{width}-{theme}.png"), full_page=True
                        )
                        print(f"OK {width}px {theme}: {route}")
                    assert not errors, errors
                    context.close()
    print(f"Screenshots: {screenshots}")


if __name__ == "__main__":
    main()
