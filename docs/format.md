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
The city figure owns names, rounded populations and roles. Taiwan's city data are
municipalities at 31 December 2025; captions for new fiches must state their own scope.

- `assets/flag.svg`: licensed flag, source and licence in the bibliography.
- `assets/relief.jpg|png|webp|svg`: optional licensed image, preferably ≤400 KB.
  Preserve proportions and terrain colours in both themes. Only reliable annotations.
- Local Natural Earth geometry renders locator and city maps.
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
