# Fiche format (data contract between content and app)

One folder per country: `fiches/<ISO3>/`.

## `fiche.md`
YAML front matter, then Markdown in French.

```yaml
iso3: TWN
iso2: TW
nom: Taïwan
nom_officiel: République de Chine (Taïwan)
capitale: Taipei
population: 23400000          # integer
superficie_km2: 36197
langues: [mandarin, hokkien taïwanais, hakka, langues austronésiennes]
monnaie: nouveau dollar de Taïwan (TWD)
regime: République semi-présidentielle
chef_etat: Lai Ching-te
date_donnees: 2026-11-15       # date the facts were checked
temps_lecture_min: 10
relief_pertinent: true         # show the relief map or not
```

Body: `##` sections in the order of `templates/fiche.md`. A section can be dropped or added when the
country calls for it (e.g. "Le phénomène du pays: les semi-conducteurs"). Prose is short and declarative.
Figures carry year and source. About 2 000 to 2 500 words.

Charts are placed with a line containing only `{{chart:<id>}}`. Maps: `{{map:locator}}`, `{{map:cities}}`,
`{{map:relief}}`. Key figures box: `{{keyfacts}}`.

## `data.json`
```json
{
  "keyfacts": [{"label": "PIB par habitant", "value": "34 400 $", "year": 2025, "source": "FMI"}],
  "indices": [{"name": "IDH", "value": 0.926, "rank": "…", "year": 2023, "source": "PNUD"}],
  "cities": [{"name": "Taipei", "population": 2500000, "lat": 25.03, "lon": 121.56, "note": "capitale"}],
  "charts": [ { "id": "climat-taipei", "type": "climate", "title": "...", "source": "...", "year": 2020, ... } ]
}
```

Chart types (all carry `id`, `type`, `title`, `source`, `year`, optional `note`):
- `climate`: `place`, `tmin` (12 °C), `tmax` (12 °C), `precip_mm` (12). Months jan→dec.
- `pyramid`: `age_groups` (labels, youngest first), `male`, `female` (same length), `unit` ("%" or "k").
- `bar` / `barh`: `labels`, `values`, `unit`. Optional `highlight` (label to emphasise).
- `stacked`: `labels`, `series` [{`name`, `values`}], `unit` (e.g. GDP by sector over years).
- `line`: `x`, `series` [{`name`, `values`}], `unit`.
- `share`: `labels`, `values` summing to ~100, `unit` "%" (languages, religions, sectors). Rendered as a
  100 % horizontal bar, not a pie.

## `assets/`
- `flag.svg`: from Wikimedia Commons (public domain), source URL in `sources`.
- `relief.jpg|png` (optional, only if `relief_pertinent`): free licence image, ≤ 400 KB, credit in `sources`.
The locator and cities maps are drawn by the app from Natural Earth data; no image needed.

## Sources
Last section of `fiche.md`: a list of every source with URL and access date.
