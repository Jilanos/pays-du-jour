# Palestine maps review, 2026-11-16

The city figure uses [Palestine location map wide.png](https://commons.wikimedia.org/wiki/File:Palestine_location_map_wide.png), by NordNordWest, CC BY-SA 3.0. Its full frame is 614 × 1141 pixels. The [English Wikipedia module](https://en.wikipedia.org/wiki/Module:Location_map/data/Palestine) gives an equirectangular projection and bounds of 33.5° N, 29.3° N, 33.7° E and 36.3° E.

`scripts/fetch_city_map.py PSE Palestine` retrieved the module and Commons metadata. The original download required a `?download=1` retry. The helper then converted the PNG to WebP. The stored image retains the original dimensions, frame, colours and aspect ratio. It occupies 28558 bytes. The bibliography describes the actual conversion without claiming a resize.

Gaza and Khan Younès initially overlapped. Their pins now use offsets `[7, -4]` and `[-7, 4]`, with leader lines. The other four pins retain their projected positions. The closest pair is Ramallah–Jéricho, separated by 25.239 units in the 260-unit SVG frame. All circles remain inside the image. No inset is needed. The population table uses 2017 locality counts and explicitly distinguishes them from current populations.

The relief image is relevant to the contrast between the West Bank hills and the Jordan Valley. The original JPEG occupies 114905 bytes. Attribution to Eric Gaba (Sting) and NordNordWest and the CC BY-SA 3.0 licence appear in the bibliography. The flag is the original Commons SVG, 281 bytes, public domain.

## Hero locator

The current regional locator and [State of Palestine (orthographic projection).svg](https://commons.wikimedia.org/wiki/File:State_of_Palestine_(orthographic_projection).svg) were compared at 400 px on light and dark backgrounds. The candidate has a useful enlarged outline, but its unlabelled globe provides less immediate regional orientation. Its bright disc dominates the dark page. Keep the regional locator, its country label and world inset. The candidate stays outside the application assets.

## Verification

`uv run pytest`: 98 passed. `uv run python scripts/lint_fiche.py PSE`: success without warnings.

The screenshot script exercised 1280 px desktop and 390 px mobile in both themes, with JavaScript disabled. All page tiles, four city figures and four hero locators were inspected. No horizontal overflow, clipped pins or overlapping circles remain. The GDP line chart uses billions of constant 2015 dollars, converted exactly from the published millions, to keep its axis labels visible.

Evidence is stored in the AFK shots directory for job `pays-fiche-PSE`: `PSE-manifest.json`, full pages and tiles, dedicated city and locator captures, and `locator-current-400-*` / `locator-candidate-400-*` comparisons.
