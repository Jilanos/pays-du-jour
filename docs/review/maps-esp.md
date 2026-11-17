# Spain maps review, 2026-11-17

## Licensed assets

The city figure uses [Spain adm location map.svg](https://commons.wikimedia.org/wiki/File:Spain_adm_location_map.svg)
by [NordNordWest](https://commons.wikimedia.org/wiki/User:NordNordWest),
[CC BY-SA 3.0 de](https://creativecommons.org/licenses/by-sa/3.0/de/).
The original SVG is 1183 × 1015 pixels and 388839 bytes. Its frame, colours and
Canary Islands panel remain intact. `scripts/fetch_city_map.py` fetched the asset
and its metadata. The Commons download query `?download=true` supplied the original
when the imageinfo URL returned HTTP 429.

The matching [English Wikipedia Spain module](https://en.wikipedia.org/wiki/Module:Location_map/data/Spain)
uses two equirectangular frames. `spain_side_map` implements its formulas:

- For longitude below -10°, x = (lon + 26.925) / 13.725 and y = (38.1 - lat) / 10.7.
- Otherwise, x = (lon + 9.9) / 14.7 and y = (44.4 - lat) / 9.7.

These are fractions of the full image. Rectangular bounds are null. Tests cover
Madrid, Barcelona, Las Palmas, both frame corners and the -10° branch boundary.
Validation rejects another module or rectangular bounds for this projection.
The five selected mainland cities need no leader-line offsets or added inset.
Their populations use INE's annual census at 1 January 2025, with municipal limits.
Coordinates come from Natural Earth's populated places dataset.

The relief figure uses [Spain rel location map.svg](https://commons.wikimedia.org/wiki/File:Spain_rel_location_map.svg),
also by NordNordWest under CC BY-SA 3.0 de. Its full Commons preview, 960 × 824 pixels,
was converted to WebP at quality 86, without cropping or recolouring. The local
file is 102424 bytes. Relief matters for the Meseta, mountain barriers and river
basins. The bibliography contains the author, licence, module and conversion.

The [flag](https://commons.wikimedia.org/wiki/File:Flag_of_Spain.svg) remains the
original 155900-byte SVG. Its authors released it into the public domain.

## Hero locator

Keep the existing regional locator. At 400 px, the Commons
[orthographic candidate](https://commons.wikimedia.org/wiki/File:Spain_(orthographic_projection).svg)
shows a much smaller Spain. The regional view keeps a legible name, neighbouring
coasts and the world inset. The globe adds a bright disc in dark mode. Neither
theme shows a clear readability gain from switching. The country map and relief
retain the island panel independently of this hero decision.

Comparison captures are `locator-comparison-ESP-light.png` and
`locator-comparison-ESP-dark.png` in the AFK shots directory for `pays-fiche-ESP`.

## Visual verification

`scripts/screenshot.sh` captured `/pays/ESP` at 1280 and 390 px in both themes,
with JavaScript disabled. All 84 page tiles were inspected, together with the
four separate city captures and four separate locator captures. Pins are distinct,
unclipped and consistent with the numbered table. No inset was added over the map.
The browser assertions found no page overflow or unloaded image.

The initial review identified an oversized precipitation scale and crowded mobile
legend labels. The final data use a common 0–120 mm rainfall scale for Madrid,
Seville and Paris. The automotive and electricity labels were shortened. All four
page captures were repeated, followed by focused inspection of those three figures
in every viewport and theme.
