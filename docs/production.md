# Producing fiches

Pilot (Taiwan, 2026-11-15): one Codex run (high power, network on) in a worktree, about 1 h.
Prompt used: `docs/prompt-fiche-twn.md`. Reuse it per country: change the country, the topics list
and the reader hooks; keep the style rules, validation steps and source rules.

Lane per batch:
1. `git worktree add -b fiche/<iso3> ../pays-du-jour.wt/fiche-<iso3>`.
2. Dispatch with `crow dispatch pays-du-jour fiche-<iso3> --cwd <worktree>` on worka or workb,
   `--power high`, max 2 runs in parallel.
3. Review: read fiche.md, check `uv run pytest`, open `/pays/<ISO3>` locally.
4. Merge `--no-ff` into main, remove the worktree and the branch.

## Existing city maps

Use a Commons country location map for every city figure. Read its English Wikipedia
`Module:Location map/data/<Country>` and the Commons file page before choosing it.
Prefer a plain map when relief obscures pins at mobile size. Check the full-frame bounds,
projection, author and licence. Accept public domain or CC BY-SA and preserve attribution.

Fetch the source and candidate JSON records from the worktree:

```sh
uv run --with cairosvg --with pillow python scripts/fetch_city_map.py MAR Morocco
```

The helper writes `fiches/MAR/assets/cities.svg|webp` and prints a `cities_map` record and
bibliography source. Review both, then copy them into `data.json`. It does not overwrite
`data.json`. Keep assets at most 400,000 bytes. Retain the original SVG when it fits.
Otherwise convert to WebP with colours, aspect ratio and the complete frame preserved.
The helper reads module bounds automatically for rectangular maps. For custom x/y formulas
it stops until a matching projection is implemented and tested. Reuse the reviewed USA
or China constants only with the exact matching map, for example:

```sh
uv run --with cairosvg --with pillow python scripts/fetch_city_map.py USA USA \
  --projection-from fiches/USA/data.json
```

Japan uses the reviewed `japan_side_map` projection for its Ryukyu side panel:

```sh
uv run --with cairosvg --with pillow python scripts/fetch_city_map.py JPN Japan \
  --projection-from fiches/JPN/data.json
```

See `docs/review/maps-jpn.md` for its formulas, pin checks and locator comparison.

Spain uses the reviewed `spain_side_map` projection for the Canary Islands panel:

```sh
uv run --with cairosvg --with pillow python scripts/fetch_city_map.py ESP Spain \
  --projection-from fiches/ESP/data.json
```

Never fit pins to an estimated country outline. Test known coastal and inland locations.
Use numbered pins and the existing table. Separate dense clusters with leader-line offsets
or a `cities_inset` using the same image and projection. Put the inset below the full map.
Morocco uses the Commons frame ending at 27.3° N; its northwest inset occupies its own row.
Bounds describe the image frame and do not declare a sovereignty position.

The renderer cites `cities_map.source_ids`. Its bibliography entry must contain the file
page, author, licence link, module and conversion. See `docs/format.md` for the contract.
Do not infer the map licence from the Wikipedia page's text licence.

Evaluate a Commons regional or orthographic locator at 400 px in both themes. Keep the
current regional locator when a globe makes the country too small, removes the contextual
labels or adds an unsuitable light disc in dark mode. Record the comparison when retaining
it. The six-country evaluation is in `docs/review/maps-existing.md`.

## Approximate currency cross rates

Show wages and incomes in local currency with an approximate euro equivalent. Prefer a
central-bank annual average for the data year. If the central bank does not publish the
currency, retain a sourced approximate cross rate. Use two legs for the same period,
such as local currency per USD multiplied by USD per EUR. State both sources, period,
calculation and approximation in `euro.basis` and in the bibliography. Keep the ≈ sign.
Do not remove the conversion solely because ECB or Banque de France lacks the currency.
Do not mix a current spot rate with an annual historical wage.

## Map verification

Run `uv run pytest` and `uv run python scripts/lint_fiche.py <ISO3>`. Start the app and run
`scripts/screenshot.sh URL OUT_DIR ISO3`. This writes full pages, tiles, a viewport manifest,
and separate `*-cities.png` and `*-locator.png` captures at desktop/mobile widths in both
themes. Inspect all four city captures. Verify that pins match the coast and cities, no
circles overlap or clip, inset boxes cover the intended cluster, the table matches pin
numbers, colours remain readable and pages have no horizontal overflow.
