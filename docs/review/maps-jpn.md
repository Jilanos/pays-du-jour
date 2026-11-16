# Japan map review, 2026-11-16

The city figure uses the existing [Commons map with the Ryukyu side panel](https://commons.wikimedia.org/wiki/File:Japan_location_map_with_side_map_of_the_Ryukyu_Islands.svg).
Author: Maximilian Dörrbecker (Chumwa), CC BY-SA 3.0. The source dimensions are
413 × 373. The full frame, colours and aspect ratio remain in `cities.webp`.
The production helper converted the large SVG to WebP at 1100 px wide, quality 90.
The local asset is below 400000 bytes.

The [English Wikipedia Japan module](https://en.wikipedia.org/wiki/Module:Location_map/data/Japan)
uses two equirectangular frames. It switches at latitude 30.90° N and shifts the
Ryukyu Islands into a side panel. `japan_side_map` implements those exact formulas.
Its bounds are null. The ordinary Japan location map without a side panel has
different bounds and is not used for these pins.

Reference tests cover Tokyo, Sapporo, Naha in the side panel, two frame corners and
the latitude switch. Contract tests reject a different module and rectangular bounds.
The shared asset tests cover the JPN figure, source credits, all six pins, frame limits
and a minimum distance of 22 SVG units between circles. Nagoya and Osaka are the only
colliding pair before offsets. Their leader lines preserve the geographic origins.
No extra inset is needed.

The relief figure uses Eric Gaba's [Japan relief location map](https://commons.wikimedia.org/wiki/File:Japan_relief_location_map.jpg),
CC BY-SA 4.0. Its WebP preserves the full source frame and terrain colours.
The credit identifies the conversion and the distant islands absent from the source.

The existing regional hero locator is retained. At 400 px, the
[Commons orthographic candidate](https://commons.wikimedia.org/wiki/File:Japan_(orthographic_projection).svg)
shows a much smaller Japan, removes the country label and adds a bright disc in dark
mode. The regional view keeps the archipelago readable in both themes and retains
the world inset. There is no clear gain from switching.

Evidence is in the AFK shots directory for job `pays-fiche-JPN`:
`locator-comparison-JPN.png`, the candidate metadata, four full-page captures,
84 page tiles, and the separate city and locator captures in all four variants.
All tiles and the eight dedicated captures were visually inspected. There are no
clipped or overlapping pins, missing images or horizontal page overflows.

The screenshot manifest records desktop width 1280 and mobile width 390, with
JavaScript disabled, in light and dark themes. The dedicated map tests, full pytest
suite and JPN fiche linter pass.
