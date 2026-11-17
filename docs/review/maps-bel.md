# Belgium map review, 2026-11-17

The city figure uses [Belgium location map.svg](https://commons.wikimedia.org/wiki/File:Belgium_location_map.svg),
by NordNordWest, under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0).
The original SVG is retained unchanged: 1136 × 988, 122830 bytes.
The [Wikipedia module](https://en.wikipedia.org/wiki/Module:Location_map/data/Belgium)
defines the full rectangular frame: north 51.8, south 49.2, west 2.2, east 6.9.
`scripts/fetch_city_map.py BEL Belgium` supplies the asset and metadata.

Eight pins use Natural Earth city-centre coordinates. Leuven is absent from that file;
its coordinates come from Wikidata Q118958. Populations are National Register commune
figures at 1 January 2026. Brussels shows the whole Brussels-Capital Region, 19 communes.

Brussels and Leuven were 19.7 SVG units apart; Charleroi and Namur 22.2. Leuven moves
by [10, −8] and Namur by [8, 4], each with a leader line. The closest pair is now
Ghent and Bruges, 28.9 units. No inset is needed. All pins sit inside the frame.

Keep the regional hero locator. At 400 px, the Commons candidate
[Belgium (orthographic projection).svg](https://commons.wikimedia.org/wiki/File:Belgium_(orthographic_projection).svg)
(Rob, CC BY-SA 3.0) reduces the country to a small green patch and adds a bright disc
in dark mode. The regional view keeps the name, the ring and the world inset.

Evidence is in the AFK shots directory for job `pays-fiche-BEL`: full pages, tiles,
`BEL-*-cities.png`, `BEL-*-locator.png` and `locator-comparison-BEL.png`.
