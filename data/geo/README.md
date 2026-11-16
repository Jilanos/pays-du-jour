# Natural Earth extract

Committed geometry for offline runtime use, prepared on 2026-11-15:

- `world-110m.json`: all 177 admin-0 features at 1:110 million, for world locators.
- `countries-50m.json`: the 197 countries in `data/ordre.csv`, admin-0 at 1:50 million.
  This dataset includes the Vatican. No additional 1:10 million geometry was required.

Source archives:

- https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip
- https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip

Natural Earth is [public domain](https://www.naturalearthdata.com/about/terms-of-use/).
Boundaries generally follow its default de facto representation. For Ukraine,
the complete Natural Earth Crimea polygon is transferred from RUS to UKR in both
extracts, following Ukraine's internationally recognised borders. Coastlines are
preserved. These locators do not describe the current military front line.
`recognized_ukraine` in the preparation script preserves this assignment on rebuild.
The inland reference point identifying that source polygon is Simferopol
(34.1° E, 44.95° N). Tests also check southern Crimea, Kyiv and Moscow.

Only geometry and country identifiers are retained. ADM0 identifiers are mapped
`KOS` → `XKX`, `SDS` → `SSD`, `PSX` → `PSE`. Topology-preserving simplification uses
0.02° (world) and 0.005° (country maps); coordinates are rounded to 0.001°.
The two files total about 1.5 MB. The app needs neither GIS dependencies nor network
access. Tiny countries have a locator dot when their outline is too small to see.
These extracts serve the regional and world locators. City maps use existing licensed
Commons assets and their published projections. See `docs/format.md` and `docs/production.md`.

Rebuild explicitly when updating the source data:

```sh
uv run --with pyshp --with shapely python scripts/prepare_geo.py
```

The script downloads source archives for this preparation step only. It falls back
to 1:10 million geometry if a listed country is missing at 1:50 million.
