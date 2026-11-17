# United Kingdom map review, 2026-11-17

The city figure uses the existing Commons [United Kingdom adm location map.svg](https://commons.wikimedia.org/wiki/File:United_Kingdom_adm_location_map.svg), by NordNordWest, under [CC BY-SA 3.0 de](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en).

The asset was fetched with `scripts/fetch_city_map.py GBR 'United Kingdom'` as documented in `docs/production.md`. The helper converted the oversized SVG to WebP. The local file is 82,160 bytes. The full source frame, aspect ratio and colours are retained.

The matching [English Wikipedia module](https://en.wikipedia.org/wiki/Module:Location_map/data/United_Kingdom) specifies an equirectangular projection. Its exact full-frame bounds are 61° N, 49° N, 11° W and 2.2° E. Original dimensions are 886 × 1369 pixels. The JSON stores those dimensions, bounds, author, licence and both source URLs.

Six numbered centres cover all four constituent nations. Coordinates come from Natural Earth populated places. Population counts come from ONS MYE2 for mid-2025. London uses the Greater London region; the other entries use local authorities. The figure explains the different administrative scopes. All pins are separated without offsets or an inset. London is inland on the Thames; Cardiff and Belfast sit beside their respective coasts; Birmingham and Manchester are inland; Glasgow lies in the western Central Belt.

The separate relief image explains the northern and western uplands and the rainfall contrast. It is Alexrk2's [United Kingdom relief location map.jpg](https://commons.wikimedia.org/wiki/File:United_Kingdom_relief_location_map.jpg), with NordNordWest's base map and SRTM data, under CC BY-SA 3.0. The 134,946-byte WebP preserves the full frame and terrain colours.

## Hero locator

Keep the existing regional locator. Compare it at exactly 400 pixels with Rob's [United Kingdom orthographic projection](https://commons.wikimedia.org/wiki/File:United_Kingdom_(orthographic_projection).svg), under CC BY-SA 3.0. The globe makes the country substantially smaller, removes its label and introduces a bright disc in dark mode. The regional view retains a readable country shape, label and world inset. The orthographic candidate offers no clear readability gain.

Comparison images and candidate metadata are in the job's external shots directory: `pays-fiche-GBR/locator-comparison-GBR-light.png`, `locator-comparison-GBR-dark.png` and `asset-metadata.json`. Original candidate SVG and its 400-pixel raster are preserved there.

## Validation

`uv run pytest`: 98 tests passed. `uv run python scripts/lint_fiche.py GBR`: no errors or warnings. Browser captures cover 1280-pixel desktop and 390-pixel mobile layouts in light and dark themes, with JavaScript disabled. All 84 page tiles and the eight dedicated city and locator captures were inspected. Pins are separated and fully visible; the licensed frame is complete; no inset covers the main map. The capture assertions verify image loading and absence of page overflow.
