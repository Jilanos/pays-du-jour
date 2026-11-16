# Fiche format

One folder per country: `fiches/<ISO3>/`. The application owns presentation, rounding,
France comparisons and citation navigation. Source numbers remain unrounded in JSON.

## `fiche.md`

YAML front matter followed by French Markdown. See `templates/fiche.md`.

```yaml
iso3: TWN
iso2: TW
nom: Taïwan
nom_officiel: République de Chine (Taïwan)
capitale: Taipei
monnaie: nouveau dollar de Taïwan (TWD)
langues: [mandarin, hokkien taïwanais, hakka, langues austronésiennes]
langue_principale: mandarin
region: Asie de l’Est
chapo: Two short editorial sentences, without statistics.
date_donnees: 2026-11-15
temps_lecture_min: 10
relief_pertinent: true
```

The hero owns the only H1, flag, locator and identity. Start the body at H2. Do not add
a title, identity summary or locator placeholder. Regime and leaders belong in politics.
Keep substantive topics and short declarative sentences. Avoid em dashes, “X, donc Y”
and “pas X mais Y”. Use the order in the template, adapting sections to the country.

A sourced paragraph ends with one annotation, outside its final sentence:

```markdown
Les montagnes séparent les plaines occidentales de la côte orientale. {#geographie-1 sources="S05,S06" label="Plaines et montagnes"}
```

IDs are stable, unique lowercase slugs. `sources` is a comma-separated list of JSON
source IDs; `label` names the passage in its return links. The app removes the annotation
and adds one muted, keyboard-accessible dot. No `[Sxx]`, source URL, publisher credit or
credit sentence in the reading body. Tables may use a sourced introductory paragraph.

Use `{{value:yushan}}` inline for a numeric record from `prose_values`. Do not manually
round or format numbers. Dates, historical years, counts of seats and model names can
remain literal. One reading location per metric: prose interprets the cards and charts
without repeating their values. Exact data are available inside each chart's native
“Voir les données” disclosure. Run `uv run python scripts/lint_fiche.py` to check the contract.

Block placeholders occupy a line of their own, outside code blocks:

- `{{keyfacts}}`: comparison cards and the single indices component, after `## Repères`.
- `{{chart:<id>}}`: one instance of a chart from JSON.
- `{{map:cities}}`: numbered city map and the only city population table.
- `{{map:relief}}`: optional relief image, subject to `relief_pertinent`.
- `{{sources}}`: the expanded bibliography, once, at the end. No separate Sources heading.

## Numeric records and France

```json
{
  "id": "fecondite",
  "label": "Fécondité",
  "value": 0.695,
  "unit": "enfant/femme",
  "year": 2025,
  "precision": 1,
  "coverage": "Indicateur conjoncturel · 2025",
  "source_ids": ["S14"],
  "france": "fecondite"
}
```

`keyfacts` is an array of these records. `indices` adds `name`, `acronym`, `scale_min`,
`scale_max`, `higher_is_better`, `rank` (display text), and published `precision`.
Use `note_visible` for an essential caveat, including Taiwan's unofficial HDI ranking.
`prose_values` is an object keyed by slug, containing `value`, `unit` and optional
`precision`. Its evidence belongs to the consuming paragraph's source annotation.

`france` is a key in `data/reference/FRA.json`, or an inline record with the same fields.
The shared file contains a `sources` array, a `checked` date, and indicator keys.
All comparison records have `status`:

- `comparable`: numeric values, year, coverage and source IDs. Match definition, scope,
  currency and period. Explicitly label different years and population coverage.
- `non_comparable`: `reason` and supporting `source_ids`. Do not draw a numeric comparison.
- `unavailable`: `reason`, including the missing dataset or matching definition, and any
  research sources. Never substitute zero or invent a value.

Only `comparable` records reach the page. For the two other statuses the app shows
nothing for France: no card slot, ring, bar, reference series, reason or France source.
The `reason` stays in the data as an audit trail.

Wages need matching gross/net, premiums, worker coverage, hours and currency basis.
No currency conversion can repair incompatible definitions. GDP is in common current
USD; a PPP comparison requires an explicit sourced basis. City ratios do not stand in
for a national comparator. France always uses muted blue and an outline/dashed encoding.

`app/format.py` formats all reading numbers: French commas, narrow nonbreaking thousands,
nonbreaking units, one decimal for percentages, three significant digits below a million
and for billions, one decimal for millions. Indices retain published precision.
`app/typo.py` applies French spacing to prose text nodes, leaving URLs and code intact.

## Euro equivalents

Mean and median wages and incomes show the local amount followed by an approximate
euro value: `50 600 TWD/mois (≈ 1 440 €/mois)`. The rate lives in `data.json`:

```json
"euro": {
  "currency": "TWD",
  "per_euro": 35.217054,
  "year": 2025,
  "basis": "How the rate was obtained, when it is not a direct published rate.",
  "source_ids": ["S57", "S58"]
}
```

`per_euro` is the annual average of the data year: units of local currency for one euro,
from ECB reference rates or Banque de France, otherwise a sourced cross rate explained in
`basis`. When neither central bank publishes the currency, keep an approximate cross
rate from sourced legs for the same period. State the calculation, period and
approximation in `basis` and in the cited bibliography entries. Keep the ≈ display;
do not remove euro equivalents solely because a direct rate is unavailable.
A `bar`/`barh` chart or a `prose_values` record opts in with `"euro": true`; its
unit must start with the currency code (`TWD`, `TWD/mois`). A `year` on the record must
equal the rate year, or rendering fails. The app adds the rate sources to the citation
and writes the rate and year under the first rate source in the bibliography. Raw data
tables keep the local currency only.

## Charts

Every record has `id`, `type`, `title`, `year`, `source_ids`, and preferably `subtitle`
(scope/year/unit). `note` moves to the bibliography; `note_visible` stays only when needed
to interpret the figure. `france` follows the reference contract above.

- `climate`: `place`, `tmin`, `tmax`, `precip_mm`, twelve months from January. A single
  figure may contain `places` with these fields per city. Use common temperature/rain
  scales across places; optional `temperature_extent` and `rain_max`. A Paris reference
  contains the same arrays, place, normal period and source IDs.
- `pyramid`: `age_groups` youngest first, `male`, `female`, `unit` (`personnes` or `%`).
  The app calculates percentages of both sexes combined. France must have identical
  age cohorts. Both raw series remain in the data disclosure.
- `bar` / `barh`: `labels`, nonnegative `values`, `unit`, optional `highlight` and
  `precision`. Accessible horizontal HTML rows. A France reference uses matching labels.
- `share`: `labels`, `values`, unit `%`; near-100 totals are retained, never silently
  normalized. Declare rounding gaps in `note_visible`. Up to six colours, neutral
  hatching beyond that; residual categories last. Values occur once in the HTML legend.
- `line`: increasing numeric `x`, up to four `series` (`name`, `values`); `null` means
  missing, leaving a gap. Actual time spacing. A France reference has matching `values`.
- `stacked`: `labels`, up to five `series` (`name`, nonnegative `values`), `unit`.
  Only explicitly percentage data use percentage scales. France values match series order.

SVG plots have responsive layouts, accessible titles and descriptions. CSS hides the
unused layout from display and the accessibility tree. All charts include exact data
in a keyboard-scrollable local table; the page itself must never overflow.

## Cities, assets and sources

`cities` contains `name`, raw `population`, `lat`, `lon` and `note` (economic role).
Optional `offset: [dx, dy]` per city moves its pin (with a leader line) when two pins overlap.
Optional `cities_note` replaces the note under the city map.
`cities_map` is required for every `{{map:cities}}`. Download an existing, openly licensed
country location map from Wikimedia Commons. Store it in `assets/` as SVG or WebP,
at most 400,000 bytes. Keep the original image frame, colours and aspect ratio. Do not
redraw coastlines or estimate bounds from the country's extent.

```json
"cities_map": {
  "file": "cities.svg",
  "width": 1223,
  "height": 995,
  "bounds": {"top": 36.25, "bottom": 27.3, "left": -13.55, "right": -0.6},
  "projection": {"type": "equirectangular"},
  "definition_url": "https://en.wikipedia.org/wiki/Module:Location_map/data/Morocco",
  "credit": {
    "author": "Eric Gaba (Sting)",
    "license": "CC BY-SA 3.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/3.0",
    "url": "https://commons.wikimedia.org/wiki/File:Morocco_location_map.svg"
  },
  "source_ids": ["CITYMAP"]
}
```

Read the matching Wikipedia `Module:Location map/data/<Country>` and the Commons file
page. `width` and `height` are the source image dimensions. `bounds` describe its full
frame, including margins and neighbouring countries. For `equirectangular`, x is the
fraction of longitude from left to right and y is the fraction of latitude from top
to bottom. Longitude bounds may cross the antimeridian.

A module with custom `x`/`y` formulas needs the matching projection. Never use rectangular
latitude bounds for a conic map. `equidistant_conic` implements the USA and China modules:
`radius = radius_offset - radians(lat)`, `angle = cone * radians(lon - longitude0)`,
`x% = 50 + scale * radius * sin(angle)`,
`y% = 50 + scale * y_scale * (y_offset - radius0 + radius * cos(angle))`.
Store those seven numeric parameters in `projection`, with its `type`; set `bounds` to
`null`. See the USA and CHN records. Add explicit support and reference-point tests for
any other projection before using it. Module formulas are never evaluated as code.

Japan's current module uses `projection: {"type": "japan_side_map"}` and `bounds: null`.
The renderer implements its exact two-frame formulas: above 30.90° N, longitude spans
128.24–149.27° E and latitude 45.86–30.02° N; at or below 30.90° N, longitude spans
110.43–131.44° E and latitude 39.54–23.71° N. This type requires the exact Japan module
and its map with the Ryukyu side panel. The full image frame remains unchanged.

`source_ids` are automatically cited alongside `map_sources.cities`. The bibliography
entry must link the Commons file page, author, licence, module and any conversion.
The renderer also attaches the declared author and licence to the first map source.
A missing asset, unsupported projection or city outside the map fails rendering.

Optional `cities_inset` magnifies a dense cluster on the **same image and projection**:
`{"label", "cities": [names], "center": [lon, lat], "zoom", "x", "y", "width", "height"}`.
Coordinates and offsets use the 260-unit-wide SVG frame. Its height expands to fit the
full source image and inset. Reserve 26 units at the top of the inset for its label.
Place it below the map with `y >= 8 + 244 * cities_map.height / cities_map.width`.
A dashed box identifies the enlarged area. Offsets and leader lines work in either
frame. Keep pin circles fully visible and at least 22 units apart; pins have radius 11.

Optional `map_focus: {"bbox": [lon_min, lat_min, lon_max, lat_max], "caption": "..."}` keeps only
the polygons inside the box on the **locator** (e.g. USA without Alaska and Hawaii).
The city map's frame is defined entirely by its licensed asset and projection.
The city figure owns names, rounded populations and roles. Taiwan's city data are
municipalities at 31 December 2025; captions for new fiches must state their own scope.

- `assets/flag.svg`: licensed flag, source and licence in the bibliography.
- `assets/relief.jpg|png|webp|svg`: optional licensed image, preferably ≤400 KB.
  Preserve proportions and terrain colours in both themes. Only reliable annotations.
- Local Natural Earth geometry renders the locator. Licensed assets render the city maps.
- `hero_sources`: source IDs for identity and flag.
- `map_sources`: object with `locator`, `cities`, `relief` arrays of source IDs.

```json
{"sources": [{"id": "S05", "text": "[Publisher, document title](https://example.org/document). Publication period, method and required credit."}]}
```

French reference sources are merged automatically. Only used sources appear, each once.
The consultation date appears once above the list. Each source has descriptive return
links to every paragraph/figure it supports. A marker targets the first source, with
numbered links to the other supporting entries. Targets are highlighted. Missing source
IDs and duplicate anchors fail rendering. All sources stay readable without JavaScript.
