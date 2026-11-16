# Licensed maps review, 2026-11-16

The six city figures now use existing Commons maps. Full-frame georeferencing comes
from the matching English Wikipedia location-map module. No coastline is redrawn.
The same image/projection is zoomed in the Taiwan and Morocco insets. Both insets sit
below the main image. The Morocco frame ends at 27.3° N and leaves the city cluster
large enough to read. Annaba's previous upward offset was removed to keep its pin visible.

| Fiche | Commons file | Author | Licence | Local format | Bytes |
| --- | --- | --- | --- | --- | ---: |
| TWN | [Taiwan location map.svg](https://commons.wikimedia.org/wiki/File:Taiwan_location_map.svg) | NordNordWest | CC BY-SA 3.0 | SVG | 123397 |
| USA | [Usa edcp location map.svg](https://commons.wikimedia.org/wiki/File:Usa_edcp_location_map.svg) | Uwe Dedering | CC BY-SA 3.0 | WebP | 81964 |
| CHN | [China edcp location map.svg](https://commons.wikimedia.org/wiki/File:China_edcp_location_map.svg) | Uwe Dedering | CC BY-SA 3.0 | WebP | 108146 |
| CHE | [Switzerland adm location map.svg](https://commons.wikimedia.org/wiki/File:Switzerland_adm_location_map.svg) | NordNordWest | CC BY-SA 3.0 de | SVG | 168392 |
| MAR | [Morocco location map.svg](https://commons.wikimedia.org/wiki/File:Morocco_location_map.svg) | Eric Gaba (Sting) | CC BY-SA 3.0 | SVG | 284498 |
| DZA | [Algeria location map.svg](https://commons.wikimedia.org/wiki/File:Algeria_location_map.svg) | Eric Gaba (Sting) | CC BY-SA 3.0 | WebP | 88456 |

SVG originals remain unchanged. WebP copies preserve the complete frame and colours,
at 1100 px wide, quality 90. Each fiche's `CITYMAP` source links its author, licence,
Commons file and module. These are location maps, not current administrative references.
Their boundary conventions do not express a sovereignty position.

## Hero locator decision

Keep the existing regional locators for all six fiches. Compare each current locator
and the following Commons candidate at 400 px in light and dark page backgrounds.
The comparison captures are `locator-comparison-<ISO3>.png` in the AFK shots directory
for job `pays-maps-existing`. Candidate metadata and original SVGs are stored there too.

| Fiche | Orthographic candidate | Observation at 400 px |
| --- | --- | --- |
| TWN | [Taiwan](https://commons.wikimedia.org/wiki/File:Taiwan_(orthographic_projection).svg) | The island is a tiny green sliver. The regional view keeps the country name and China/Japan/Philippines labels. |
| USA | [United States](https://commons.wikimedia.org/wiki/File:United_States_(orthographic_projection).svg) | The globe is legible but the country occupies less of the frame. It adds no clear gain over the regional view and world inset. |
| CHN | [China](https://commons.wikimedia.org/wiki/File:China_(orthographic_projection).svg) | The globe is legible. The current regional map uses more area for China and neighbouring coastlines. |
| CHE | [Switzerland](https://commons.wikimedia.org/wiki/File:Switzerland_(orthographic_projection).svg) | The country is only a small mark. The regional locator has a visible ring and name. |
| MAR | [Morocco](https://commons.wikimedia.org/wiki/File:Morocco_(orthographic_projection).svg) | The country becomes a narrow patch. Hatching for Western Sahara is difficult to distinguish at this scale. |
| DZA | [Algeria](https://commons.wikimedia.org/wiki/File:Algeria_(orthographic_projection).svg) | The regional map gives much more space to Algeria and its immediate surroundings. |

The globe candidates keep a bright disc in dark mode. The existing locators use the
page palette and retain the labelled country and world inset. None has a clear overall
readability advantage sufficient to justify replacing the locator. This decision applies
to the hero only. The city figures use the licensed country maps listed above.

## Verification

`uv run pytest` exercises projection reference points, all six assets and bibliography
credits, pin separation, map bounds, inset clipping and malformed records. The asset
limit is 400000 bytes. The USA and China projections retain their module constants.
The other four maps use the exact published rectangular bounds.

`scripts/screenshot.sh` captures every fiche at 1280 px and 390 px in both themes, with
JavaScript disabled. Its assertions check page overflow, font readiness and image loading,
including the external images embedded in SVG. Dedicated city and locator screenshots
supplement full-page images and tiles. The city captures are reviewed in all four variants.
The fiche linter returns success for all six. DZA retains a pre-existing warning about
the 65-plus metric repeated in prose. It is unrelated to maps.
