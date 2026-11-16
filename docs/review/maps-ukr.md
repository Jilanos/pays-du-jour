# Ukraine map review, 2026-11-16

## City map

Use the image currently named by the English Wikipedia
[Ukraine location-map module](https://en.wikipedia.org/wiki/Module:Location_map/data/Ukraine):
[Ukraine administrative locations map, improved.svg](https://commons.wikimedia.org/wiki/File:Ukraine_administrative_locations_map,_improved.svg).
The Commons page credits Yakiv Gluck and TUBS under CC BY-SA 4.0.

`scripts/fetch_city_map.py UKR Ukraine` downloaded and converted the original with
the documented CairoSVG/Pillow environment. The original frame is 3780 × 2540.
Bounds are 52.7° N, 44.1° N, 21.5° E and 40.7° E, equirectangular projection.
The 1100-pixel-wide WebP preserves the complete frame, colours and aspect ratio.
Its size is 79212 bytes. The flag SVG is the unchanged 182-byte Commons original.

The six city populations are administrative-city estimates at 1 January 2022.
They are explicitly labelled as predating the full-scale invasion. Coordinates
come from Natural Earth populated places. Dnipro and Zaporizhzhia are the only
pins with offsets, to separate their colliding circles. All circles remain at
least 22 SVG units apart. There is no inset. The image, pins and table were
inspected at 1280 and 390 pixels in both themes.

## Hero locator

Retain the regional locator. Compare it at 400 pixels in light and dark themes
with [Ukraine (orthographic projection).svg](https://commons.wikimedia.org/wiki/File:Ukraine_(orthographic_projection).svg),
M.Bitton, CC BY-SA 4.0. On the globe Ukraine occupies a small part of the frame.
The regional view keeps its shape, name, Black Sea context and world inset
legible. The globe adds a bright disc in dark mode. It offers no clear
readability gain.

The existing Natural Earth extracts assigned Crimea to Russia under their default
de facto convention. Both locator extracts now transfer the entire source Crimea
polygon from RUS to UKR. The original coastlines and combined area are preserved.
The regional locator and its world inset identify Ukraine within internationally
recognised borders. They do not represent military control or a front line.
No other country geometry is changed.

`recognized_ukraine` in `scripts/prepare_geo.py` preserves the assignment on
rebuild. It identifies the isolated source polygon using an inland Simferopol
point and fails if the source representation changes. Both original source
archives were downloaded separately to verify that the transfer preserves their
combined geometry. Regression tests cover inland Crimea, southern Crimea, Kyiv
and Moscow at both resolutions. The city map uses its own licensed Commons image.

## Evidence

Captures, the Commons candidate and its metadata are in the AFK shots directory
for `pays-fiche-UKR`. `locator-comparison-light.png` and
`locator-comparison-dark.png` show both candidates at 400 pixels.

`scripts/screenshot.sh` captures all four desktop/mobile and light/dark variants,
full pages, 1500-pixel tiles, city figures and locators. The manifest records
viewport width and disabled JavaScript. The assertions check horizontal overflow,
font readiness and loaded images. All tiles and the dedicated map captures were
reviewed. `uv run pytest` passes 93 tests, including UKR city-map separation,
asset limits, citations and Crimea regression checks. The UKR fiche linter passes.
