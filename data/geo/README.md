# Natural Earth extract

Committed geometry for offline runtime use, prepared on 2026-11-15:

- `world-110m.json`: all 177 admin-0 features at 1:110 million, for world locators.
- `countries-50m.json`: the 197 countries in `data/ordre.csv`, admin-0 at 1:50 million.
  This dataset includes the Vatican. No additional 1:10 million geometry was required.

Source archives:

- https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip
- https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip

Natural Earth is [public domain](https://www.naturalearthdata.com/about/terms-of-use/).
Boundaries follow its default de facto representation. They are not a position on
recognition or sovereignty.

Only geometry and country identifiers are retained. ADM0 identifiers are mapped
`KOS` → `XKX`, `SDS` → `SSD`, `PSX` → `PSE`. Topology-preserving simplification uses
0.02° (world) and 0.005° (country maps); coordinates are rounded to 0.001°.
The two files total about 1.5 MB. The app needs neither GIS dependencies nor network
access. Tiny countries have a locator dot when their outline is too small to see.
City maps use an equirectangular projection with local latitude correction and wrap
longitudes around the shortest interval for countries crossing the date line.

Rebuild explicitly when updating the source data:

```sh
uv run --with pyshp --with shapely python scripts/prepare_geo.py
```

The script downloads source archives for this preparation step only. It falls back
to 1:10 million geometry if a listed country is missing at 1:50 million.
