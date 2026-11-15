# Pays du jour: design specification

Review, 15 November 2026. Preserve the length, subjects, server rendering and reading without JavaScript. Direction: a contemporary editorial atlas, with warm paper, expressive headings and precise graphics.

Inspected all 45 tiles in `shots/before/`: `twn-desktop-00–14.png`, `twn-mobile-00–16.png`, `home-desktop-00–04.png`, `home-mobile-00–07.png`; also the brief, format, templates, renderers and Taiwan content. Additional viewport captures: `shots/review-codex/`.

**Evidence and priorities**

- **P0:** `twn-desktop-00.png` repeats the title and identity; `02–03` repeats indices. `01` and `09` repeat city populations. Source lines compete with every component; paragraphs repeatedly display Sxx links.
- **P0:** `twn-mobile-02–03.png` splits numbers and headings into fragments. Supplied mobile tiles also crop the right edge. Actual 390px browser checks show no page overflow; at 320px, the fiche reaches 340px. Fix narrow tables; correct screenshot viewport capture before judging clipping.
- **P1:** `twn-desktop-00–02.png`: nearly invisible locator, crowded northern city labels, oversized unannotated relief. `03–08`: awkward ticks, undersized mobile labels, excessive chart padding; religion colours repeat. `10–12`: little rhythm between prose sections.
- **P2:** `home-desktop-00–04.png` and `home-mobile-00–07.png` resemble a production queue: mostly “à venir”, no visual invitation to open Taiwan.

**P0: structure and unique ownership**

Order: hero → comparison panel → geography/climate with relief/cities → population → everyday life → wealth/economy → history/politics/current affairs → culture → France → semiconductors → curiosity → sources. Keep every substantive topic. Assign every metric one reading location across cards, charts, tables and prose.

Hero: 64px flag beside one H1; official name below; two-sentence editorial introduction without statistics. Show capital, currency and principal language in a compact definition list. Move regime/leader to politics, language detail to population. Reading time and French verification date share one quiet line. Place locator alongside at ≥900px, below otherwise. Remove Markdown H1, quotation-summary and separate “Carte” section.

Comparison panel owns population, area, nominal GDP, fertility, 65+ share and imported energy. Two metric cards per row above 700px; one below. Each card: 14px label; two equal columns labelled “Taïwan” and “France”; 28px values; 14px units/year. Example: `Population | Taïwan: 23,2 millions | France: {verified value}`. No invented comparison values. Prose explains these figures without repeating them.

Use numeric records with `id`, `value`, `unit`, `year`, `precision`, `coverage`, `source_ids`, optional `france` using the same fields. Match definition, territory, period and currency; show differing years explicitly. Missing: “France : donnée indisponible”; incompatible: “France : non comparable”, with a short reason. Wages require matching gross/net and worker coverage; monetary comparisons require a documented common currency basis.

Render indices once, from `data.json`, after the comparison panel: `Indice / Taïwan / France / Année`. Put scale, direction and rank beneath the corresponding label/value. Preserve Taiwan’s unofficial HDI-ranking caveat. Below 600px, use labelled comparison rows with the index heading above two value columns. Remove the second Markdown table. Keep explanatory caveats, never source columns or composite scores.

**P1: visual system**

Use [Fraunces](https://fonts.google.com/specimen/Fraunces) 500 for H1/H2 and [Source Sans 3](https://fonts.google.com/specimen/Source+Sans+3) 400/600 for body, UI and graphics; self-host WOFF2, `font-display: swap`, Georgia/system fallbacks. Desktop/mobile sizes: H1 64/44, H2 34/28, H3 21/20, body 19/18, metadata 14px. Body line-height 1.7; headings 1.15; tabular numerals for data.

| Token | Light | Dark |
|---|---|---|
| background | #FAF8F3 | #151E20 |
| surface | #F0EDE5 | #202C2F |
| ink | #202C2F | #F1EFE7 |
| muted | #59666A | #ADB9BA |
| rule/grid | #D6DAD4 | #405055 |
| accent/country | #176B64 | #7ED3BD |
| France | #526B9A | #A8BDE8 |
| map land | #D4DDD4 | #445957 |

Layout: maximum 1152px content shell excluding gutters, article up to 880px, 240px TOC, 32px gap; prose capped at 66ch. Header/footer align with shell. Gutters 32px desktop/20px mobile. Spacing scale: 8/16/24/32/48/72px. Sections start after 72/48px with a fine rule and small chapter number. Sticky TOC above 1200px; native mobile `<details>`. Preserve subsection anchors.

Figures: 24/16px padding, 8px corners, surface background, no shadow. Tables: 16px text, 12px vertical padding, horizontal rules, right-aligned unbroken numbers, wrapping labels. Contain wide tables within labelled scroll regions. Callouts: 3px accent edge, 24px padding, one takeaway; style the final curiosity this way. History gets a vertical dated timeline.

**P1: shared chart contract**

Title, then scope/year/unit, then plot; retain essential interpretation caveats. Move provenance entirely to sources. Native “Voir les données” exposes exact values within the same component. SVG gets a meaningful title/description.

Categorical light/dark pairs: teal #176B64/#7ED3BD, blue #276AA5/#88B9EF, ochre #8B6516/#E6C16B, purple #79529E/#C8A2E4, rust #A94F34/#F29B7F, grey #59666A/#ADB9BA. Beyond six categories, use distinct neutral hatch patterns. Keep category colours consistent across related charts. Add shapes/dashes and direct labels in ink colour; legends only for stacks/shares. France always uses its token plus dashed lines or hollow markers.

Use 1px subdued gridlines, 3px series, 4–5 ticks on 1/2/5-based intervals. Bars start at zero. French decimal commas, narrow nonbreaking thousands/unit spaces: `4,0 millions d’habitants`, `36 200 km²`, `20,8 %`, `0,7 enfant/femme`; retain index precision needed for interpretation. Units appear once per axis; never bare “k”.

Generate desktop/mobile SVG layouts selected through CSS at 600px, with unique IDs and only the visible version exposed. At 320px, rendered labels stay ≥14px; apply this to maps too. Plots use 300–360px height; pyramid ≥540px. Wrap HTML legends; reserve label gutters instead of shrinking text.

| Type | Required redesign |
|---|---|
| climate | Two aligned panels per city: temperature min/max lines above rainfall bars. Common Taiwan scales: 0–40 °C, 0–600 mm. Other countries expand scales as needed. Mobile month initials with full names in data. Optional Paris panels use identical normals and scales; label Paris explicitly. |
| pyramid | Symmetric axes, centred age labels, oldest above; percentages of total population for comparison. Country bars plus French outline bars; identical cohorts/year. Keep all cohorts. |
| bar | Salary median/mean pairs, direct rounded values above bars, ≤64px bar width. France hollow companion bars only with compatible definitions. |
| barh | Housing rows with labels above bars on mobile, end values, 0/5/10/15-year ticks. Comparable national France reference is dashed; distinguish city comparisons. |
| stacked | Stable sector order/colours across years; absolute totals above stacks. Normalize only explicitly percentage data. France in an adjacent panel with identical scale. |
| line | Actual time spacing; gaps for missing values; ≤4 series, labelled endpoints with collision spacing. France dashed; no smoothing. Mark any nonzero baseline clearly. |
| share | 32px horizontal 100% strip plus wrapping HTML label/value list, values once. Separate matching France strip. Preserve published rounding gaps; disclose totals such as 99%, never silently normalize. |

`stacked` and `line` are supported but absent from Taiwan; their specifications cover future fiches.

**P1: maps**

Locator: 400×260 regional East Asia view plus 120×70 world inset. Mark Taiwan with a minimum 8px ring and label; label China, Japan, Philippines and surrounding seas. Keep the world context visible on mobile.

Cities: neutral land, numbered pins, northern inset for Taipei/New Taipei/Taoyuan, north arrow and 100km scale. One adjacent table owns names, rounded populations and economic roles; stack beneath on mobile. Delete the duplicate city list/table elsewhere.

Relief: cap height at 440/340px; preserve proportions. Annotate central mountains, western plain and Yushan; include scale/north and an altitude legend only when supported by the underlying asset. Keep natural terrain colours in dark mode. Put credits/licence at the bottom.

**P0: sources rendering**

No Sxx text, source captions or attribution paragraphs in the reading body. Only section headings carry `<sup><a href="#sources-climat" aria-label="Sources : climat">·</a></sup>`: 12px muted dot, 24px hit area, visible focus.

Bottom sources remain expanded, grouped by section: H3 plus ordered list, 15px/1.5 text, 16px between entries. Each entry: linked publisher/title, publication/data period, consultation date, then descriptive back-links, e.g. `↩ Taipei : climat · ↩ Kaohsiung : climat`. Links target stable paragraph/figure IDs. Repeat an entry across section groups when necessary; every source receives its relevant back-links. Apply `:target` highlighting. Include map/flag credits and adaptation details here.

**P2: browsing and acceptance**

Home: feature Taiwan with flag, locator crop, one editorial sentence and “Lire la fiche”. Follow with all 197 countries in 3/2/1 columns at ≥1100/700/<700px. Each ≥64px row shows name, thematic group and availability. Keep forthcoming countries readable and noninteractive. Rename “Par palier” to “Par affinités”; retain ordering. Add GET search, availability filter, group jumps and A–Z anchors; default shows everyone. End fiches with next available country and index links.

Accept at 320/390/768/1280px, both themes, 200% zoom and JavaScript disabled: one H1, no page overflow, readable chart labels, working source round-trips, unique visible figures and meaningful France comparisons. Adapt `scripts/check_browser.py` to actual Taiwan content; validate screenshot viewport dimensions.

Implementation ownership: `content.py` handles numeric formatting and source/anchor mapping; templates/CSS handle layout; `charts.py` and `maps.py` handle responsive graphics. Revise the format contract and Taiwan Markdown together to eliminate duplicate presentations.
