# Netherlands map review, 2026-11-16

The city figure uses [Netherlands location map.svg](https://commons.wikimedia.org/wiki/File:Netherlands_location_map.svg),
by Lencer, under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0).
The original SVG is retained unchanged: 888 × 1001, 142739 bytes.
The [Wikipedia module](https://en.wikipedia.org/wiki/Module:Location_map/data/Netherlands)
defines the full rectangular frame: north 53.7, south 50.6, west 3.1, east 7.5.
`scripts/fetch_city_map.py NLD Netherlands` supplies the asset and metadata.

The six pins use Natural Earth city-centre coordinates and CBS municipal populations
at 1 January 2025. Amsterdam, Rotterdam, The Hague and Utrecht occupy a separate
Randstad inset. It magnifies the same image four times. Its top is at y=292, below
the full map, whose bottom is at about y=283. Pins remain separated by at least
22 SVG units. No leader offsets are necessary. Eindhoven and Groningen remain in
the main frame. The map and statistics describe the European Netherlands.

Keep the regional hero locator. At 400 px, the Commons candidate
[Netherlands (orthographic projection).svg](https://commons.wikimedia.org/wiki/File:Netherlands_(orthographic_projection).svg)
reduces the country to a small green mark. The current view retains a visible country,
its name and the world inset. Its palette remains legible in both themes. The globe
adds a bright disc in dark mode without a readability gain.

Verification: 90 repository tests pass. The existing licensed-map check was also run
directly against NLD, covering full-frame projection, asset credit, inset placement,
pin separation and clipping. The fiche linter passes without warnings. The complete
HTTP response has unique anchors and no missing internal citation targets.

The screenshot script passed at 1280 px and 390 px, light and dark, without JavaScript.
All 82 tiles were inspected, together with the four city captures and four locator
captures. The climate chart uses a local 0–100 mm rainfall scale and a 0–30 °C
temperature scale. The changed chart was inspected again in all four variants.
The final pages have no horizontal overflow or missing images.

Evidence is stored in the AFK shots directory for job `pays-fiche-NLD`:
`NLD-manifest.json`, `review-tile-manifest.json`, the full pages and individual tiles,
`NLD-*-cities.png`, `NLD-*-locator.png`, and `locator-comparison-NLD.png`.
