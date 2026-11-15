# Design synthesis (2026-11-15)

Two independent reviews: `design-claude.md` (Claude Opus) and `design-codex.md` (Codex gpt-6-astra).
They agree on most points. Implement both, with these arbitrations where they differ:

| Topic | Decision |
|---|---|
| Fonts | Fraunces (headings) + Source Sans 3 (body, UI, charts), self-hosted woff2, latin + latin-ext. |
| Colour tokens | Codex table (light/dark), France always its own muted blue token, never the country accent. |
| Hero | Codex: flag + single H1 + official name + 2-sentence intro, compact capital/currency/language list, reading time + date line. Regime/leader move to politics. |
| Key figures | One "Repères" panel, Taïwan vs France per card (Claude's two small bars per card are welcome). Prose does not repeat these numbers. |
| Indices | Shown once, Claude's row design (name, 0–max scale with country dot and hollow France ring, rank, year). Keep the HDI caveat. |
| France data | `data/reference/FRA.json`, keyed by indicator, same definitions/years where possible; "non comparable" or "indisponible" with a reason instead of an invented value. |
| Rounding | `app/format.py` used everywhere; data stores raw numbers. French typography filter (Claude, `app/typo.py`). |
| Sources | Owner asked: sources at the bottom, linked to the paragraph. One discreet muted marker per paragraph or figure (Claude), linking to the bottom list; each bottom entry has back-links named after the paragraph/figure (Codex wording `↩ Taipei : climat`). No source lines, captions, Sxx text or credit paragraphs in the body. `:target` highlight. |
| Charts | Shared style guide from both. Bar / barh / share as accessible HTML rows when that reads better on mobile (Claude); SVG with mobile variant otherwise (Codex). France reference (dashed / hollow) when the definition is comparable. Climate: aligned panels, common scale, optional Paris reference. Pyramid in % with France outline. |
| Locator | Codex: regional view + world inset, ring and labels, readable on mobile. |
| Cities | Codex: numbered pins, inset for dense north, one table owning names/rounded populations/roles. Fix `maps.cities()` replacing commas. |
| Relief | Height cap, annotations only if reliable, credit in sources. |
| Home | Both: featured fiche card, 197-country index inviting browsing, "Par affinités" naming, flags, no JS needed. Claude's clickable world map if cheap. |
| Fiche end | Next available country + back to index. |
| Screenshots | Fix `scripts/screenshot.sh` mobile capture (Windows Chrome has a minimum window width): use device emulation (e.g. Playwright via uv, or Chrome DevTools mobile emulation). |
