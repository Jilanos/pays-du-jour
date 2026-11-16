# Israel fiche and map review, 2026-11-16

The fiche uses the existing components and contains about 2,250 French words,
seven charts, six key facts and five indices. Political reporting stops on
16 November 2026. The government formation mandate is distinguished from an
investiture.

## City map

The [English Wikipedia module](https://en.wikipedia.org/wiki/Module:Location_map/data/Israel)
selects [Israel location map with stripes.svg](https://commons.wikimedia.org/wiki/File:Israel_location_map_with_stripes.svg).
Drink L’Chaim adapted NordNordWest’s location map. Both contributors are credited
in the bibliography under CC BY-SA 3.0. The helper `scripts/fetch_city_map.py`
downloaded the original SVG without conversion, cropping or recolouring.

- Original dimensions: 614 × 1141.
- Full-frame bounds: north 33.5, south 29.3, west 33.7, east 36.3 degrees.
- Projection: equirectangular, with the original image’s north-south stretching.
- Asset: `fiches/ISR/assets/cities.svg`, 174166 bytes.
- Numbered centres: Jerusalem, Tel Aviv-Jaffa, Haifa and Beer-Sheva.
- Coordinates: Natural Earth populated places, 1:10m.
- Minimum pin separation: 52.61 SVG units, above the 22-unit minimum.
- No pin offsets or inset are needed. All pin circles fit within the frame.

Municipal populations come from CBS table 2.15, 31 December 2024. The source
publishes thousands with one decimal; the stored counts multiply these values
by 1000. Foreign residents are included. Jerusalem includes East Jerusalem.
The caption explains the territorial conventions and distinguishes the map
from current military control lines.

The physical map is relevant to the coastal plain, highlands, Jordan depression
and Negev. `relief.jpg` retains the original 614 × 1141 frame and colours,
183153 bytes. Eric Gaba (Sting) and NordNordWest are credited under CC BY-SA 3.0.
The original public-domain flag SVG is 398 bytes.

## Hero locator

Keep the regional locator. It was compared at an exact width of 400 pixels in
both themes with [Israel (orthographic projection).svg](https://commons.wikimedia.org/wiki/File:Israel_(orthographic_projection).svg),
by Sammy pompon, CC BY-SA 3.0. The globe leaves Israel as a tiny green mark and
adds a bright disc in dark mode. The current map retains the labelled ring,
regional context and world inset. The candidate offers no clear readability gain.

The comparison captures are `locator-comparison-400-light.png` and
`locator-comparison-400-dark.png` in the AFK shots directory for job
`pays-fiche-ISR`. The original candidate SVG is retained there for inspection.

## Validation

`uv run pytest`: 93 passed. `uv run python scripts/lint_fiche.py ISR`: success
without warnings. A separate geometry check verified all four circle bounds,
minimum separation, asset sizes and the demographic pyramid total.

The app ran on port 8046. `scripts/screenshot.sh` captured the page at 1280 and
390 pixels, in light and dark themes, with JavaScript disabled. All 80 page
tiles were inspected, including bibliography tiles. The four separate city
captures and four separate locator captures were inspected. Images load,
colours remain readable, pins do not overlap or clip, and the page has no
horizontal overflow.

France comparisons use matching WDI definitions and years for population,
GDP, fertility, age structure and sectoral value added. New French GDP and
fertility records for 2024 are sourced in `data/reference/FRA.json`. National
wage and Gini definitions are not harmonised, so those French comparisons are
omitted. Wages retain local amounts and approximate euro equivalents using
the direct ECB annual average for 2025.

The mother-tongue chart explicitly retains the 2011 survey date. The Bet Dagan
CSV provides temperature normals but no precipitation-total series in the
retrieved edition. The complete climate chart uses Jerusalem’s WMO station.
No missing rainfall values were filled or inferred.
