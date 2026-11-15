# Design review: fiche and home (reviewer: claude)

Sources: every tile in `shots/before/`, plus `app/` and `fiches/TWN/`. **P0** = fix first, **P1** = core redesign, **P2** = polish.

## 1. Problems in the screenshots

| Tile | Problem |
|---|---|
| twn-desktop-00 | The title block appears twice: the hero, then Markdown `# Taïwan` plus a blockquote that repeats capital, population, area and currency. The date is in ISO format. The `TWN` eyebrow means nothing to a reader. |
| twn-desktop-00 | The header is centred on 808 px and the content on 1140 px, so their left edges don't line up. |
| twn-desktop-00 | Locator: on the flat world map, Taiwan is a 3 px sliver. |
| twn-desktop-01 | Cities map: a dark teal blob, overlapping labels (Nouveau Taipei/Taipei/Taoyuan), crossing leader lines. The legend is bigger than the caption. The city list repeats the table on desktop-09. **Bug:** `maps.cities()` turns every `,` into U+202F ("Couronne métropolitaine  industrie"). |
| twn-desktop-01/02 | The relief image is about 1 100 px tall, with no frame. Its credit is buried in prose. |
| twn-desktop-02/03 | The same figures appear up to 4 times. Population shows as 23 204 000, 23,204 millions and 23 299 132. |
| twn-desktop-02, mobile-02 | The indices table splits digits ("0.93/4", "Vale/ur") because of `overflow-wrap:anywhere`. It uses a decimal point. The keyfacts use Georgia old-style figures, and their source lines are longer than the values. |
| twn-desktop-03/04 | Climate: tick values are max÷4 (8,7 / 17,4 / 87,5). The chart uses a dual axis. "Août Sep" collide. The legend says "(tirets)". The title repeats the place. The two cities use different scales. |
| twn-desktop-04/05/07/08 | Pyramid ticks at 510,1 / 1 020,3 with a bare "k". Salary ticks at 12 660,8, with about 120 px of empty space and arbitrary colours. Barh ticks at 3,7 / 7,4. |
| twn-desktop-05/06/08/11 | Share charts: a thin bar plus a legend list. The 0 %/100 % labels are useless. Religions reuse two colours. |
| all figures | Each figure carries 4 layers of meta: title, source, note and data toggle. |
| all prose | `S12, S13` links are the most visible links on the page. |
| twn-mobile-12 | "Le phénomène du pays / : les semi-conducteurs": the colon wraps to the start of the line. |
| twn-desktop-13/14 | "Consulté le 15/11/2026" is repeated 56 times. |
| home-desktop-00..03 | 196 grey "à venir" rows in zig-zag row order. No flags, no map, and nothing points to the one available fiche. |
| twn/home-mobile-* | The right edge is clipped. The identity grid (columns at x=20 and x=257) implies a layout about 490 px wide cropped to 390. Windows headless Chrome has a minimum window width, so this is likely a capture artefact. Re-shoot with device emulation (Playwright viewport 390×844) before judging mobile. |

## 2. Structure, hero, rounding (P0)

Order: hero, chapô, Repères, Indices, sections, Sources.

**One place per figure.** Drop `# Taïwan`, the blockquote and the Markdown indices table.
- The hero holds identity only: capital, population, area, languages, currency, regime, head of state.
- Repères holds other figures only, never population or area.
- Indices is a single component.
- `scripts/lint_fiche.py` warns when a keyfact or index value appears verbatim in the prose or in a chart note.

**Hero.** Two columns at ≥ 900 px, stacked below that.
- Left: flag 64 px tall with a 1 px `--rule` outline. Eyebrow "Asie de l'Est · 10 min de lecture". Then the h1, the official name in italic serif `--ink-2`, and an optional `chapo` front-matter field at 1.3rem.
- Identity `dl` on a 4-column grid (2 on mobile). Labels in Inter .75rem uppercase, muted. Values in serif 1.15rem. Population and area show the France value below ("France 68,6 M", muted .8rem).
- Right: globe locator (§5).
- Last line: "Données vérifiées le 15 novembre 2026", using a `date_fr` filter.

**Rounding.** `app/format.py` is used everywhere. Data stores raw numbers, never hand-typed strings.
- ≥ 1 M: "4,0 millions" (in charts: "4,0 M").
- ≥ 1 Md: 3 significant digits, "922 milliards $".
- Below that: 3 significant digits, "36 200 km²".
- %: 1 decimal at most. Indices keep their published precision.
- Thousands separator U+202F, decimal comma, U+00A0 before units.

**Typography filter** (`app/typo.py`, on text nodes): U+00A0 before `:` and inside « », U+202F before `; ! ? %`.

## 3. Key figures and France comparison (P1)

**Data**
- `data/reference/FRA.json` is keyed by indicator id, `{value, year, sources}`, plus `climat-paris` and `pyramide-france`. Its sources merge into each fiche's list.
- `keyfacts[]`: `{id, label, value, unit, format, year, sources, france}`.
- `indices[]`: `{id, name, value, scale_min, scale_max, higher_is_better, rank, rank_of, year, sources, france}`.
- Charts take an optional `france` ref.

**Repères.** Grid `repeat(auto-fill,minmax(200px,1fr))` with a 1 px gap on a `--rule` background, so the cells read as a hairline mosaic.
- Label in Inter .8rem, muted, followed by the source marker.
- Value in Source Serif 2.25rem, weight 600, lining tabular numerals. Unit in .9rem sans.
- Two 6 px bars on a shared scale: country `--accent`, France `--france`, with "France 2,1 M" at .75rem.
- Year at .7rem. No source text.

**Indices.** One row each, on a grid `12rem 1fr 4.5rem`: name | scale | rank.
- Scale: a 4 px `--rule` track from `scale_min` to `scale_max`.
- Country: 12 px `--accent` dot with its value above. France: 10 px hollow `--france` ring labelled "FR".
- Gini (`higher_is_better=false`) shows "← plus égal".
- Rank shows as "28ᵉ / 180". An unofficial rank is set in italic, with a `title` explaining why.
- On mobile, the name sits above a full-width scale.

## 4. Visual system (P1)

**Fonts.** Self-hosted woff2, latin + latin-ext.
- **Source Serif 4** (variable, opsz) for headings and body.
- **Inter** for UI, labels, tables, charts and figures, with `tabular-nums`.

**Scale** (body 19 px, 17.5 px at ≤ 540 px)
- h1: clamp(2.6rem,6vw,4.25rem)/1.02, weight 600, tracking −.015em.
- h2: serif 1.75rem/1.2, weight 600, with an Inter .75rem accent eyebrow "03".
- h3 and figure titles: Inter 1.05rem, weight 600.
- Body: serif 1rem/1.62, max 66ch, `hyphens:auto`, `text-wrap:pretty`.
- Meta: Inter .8125rem.

**Tokens** (light / dark)
- bg #FBFAF7/#121614 · surface #F3F1EC/#1A201E · ink #1B2220/#E9EDEA · ink-2 #48524E/#B9C3BE · muted #6B7571/#8F9A95 · rule #E3DFD7/#2B3431
- accent (country) #1E6158/#7CC7B6 · accent-soft #E2EEEA/#1D3530 · **france #8C929B/#A4AAB3**
- warm #C2502F/#F08C6C · cool #2F6E9E/#7FB5DC · rain #A9C1DC/#35506E
- cat-1..6 light: #1E6158 #C98A2B #5B6FB5 #B4544E #6E8F3E #8A6AA8
- cat-1..6 dark: #7CC7B6 #E6B160 #97A7E6 #E68A84 #A9C979 #BFA1DB

SVGs use `var(--…)` only.

**Layout**
- One grid with named lines `full | wide (920) | text (680)`. The header and footer sit on it too (fixes the misalignment).
- At ≥ 1240 px, a sticky numbered TOC rail, 220 px wide.
- Gutters: 20 px on mobile, 32 px on desktop.
- Sections: margin-top 4.5rem, under a 40×3 px `--accent` rule.
- Figures: wide, margin 2.5rem.

**Tables**
- No fills and no vertical rules. Header in Inter .72rem uppercase, muted, with a 2 px `--ink` bottom rule. 1 px row rules.
- Numbers right-aligned and tabular, with `overflow-wrap:normal`.
- The leaders table uses `width:auto`.
- On mobile, the cities table's "Repère" cell wraps to its own line.

**Callouts**
- "Le saviez-vous ?" sits on an `--accent-soft` panel, radius 4 px.
- Paragraphs that start with `**YYYY.**` render as a timeline: a 5rem accent year column and a 2 px left rule.

## 5. Charts and maps (P1)

**Style guide**
- **Legible on mobile.** bar, barh and share become HTML/CSS rows with real text. climate, pyramid, line and stacked render two SVG layouts (720 and 360 wide, with fewer ticks and short labels on the narrow one), swapped by a media query.
- Text: Inter, 13 px equivalent. Labels `--ink-2`, values in `--ink` weight 600.
- **Nice ticks:** 1-2-5 steps, 3 to 5 ticks. Horizontal gridlines only, 1 px `--rule`, with a 1.5 px baseline. No axis lines.
- Units go in the subtitle, never in an axis corner.
- **Label directly**; legends only as inline swatches above the chart.
- French numbers come from `format.py`. Months: "janv. févr. … déc.", initials on the 360 layout.
- **France is always `--france`:** dashed 4 3 lines, hollow or outlined bars and dots, labelled "France".
- Figure: a statement title, a one-line subtitle, the chart, then "Données ▸" right-aligned. No source line. Notes move to the source list, except an optional one-line `note_visible`.

**Per type**
- **climate:** small multiples on shared scales, one figure for all cities.
  - Top band: tmin–tmax filled `--warm` at .18 opacity, with tmax and tmin lines.
  - Bottom: `--rain` bars on their own scale, so there is no dual axis.
  - Paris overlay: thin dashed lines plus grey rain ticks.
  - Label only the hottest month and the wettest month.
- **pyramid:** in % of total. Male `--cool` on the left, female `--warm` on the right, 2 px gaps, age labels every 10 years. France as a 1.5 px step outline. Ticks 0/2/4/6 %. Annotate the 65+ share once.
- **bar:** horizontal rows, with a 6 px France bar under each country bar and the value at the bar end. Money in € at PPP, with the local currency muted beside it.
- **barh:** label 30 %, bar 55 %, value 15 %. The highlighted bar is `--accent`, the rest `--accent` at 45 %. Add a France row. No ticks.
- **stacked:** 100 % columns, or areas when there are 6 or more periods. At most 5 series, labelled at the right end. France column after a 24 px gap.
- **line:** country 2.5 px `--accent`, France 1.5 px dashed, others `--cat-*`. End labels "Nom 12,3" in a 120 px margin, with a dot on the last point only.
- **share:**
  - A 32 px HTML bar, sorted descending, with "Autres" last in `--muted` and 2 px gaps between segments.
  - Label segments of 9 % or more inside the bar, the rest in a row below.
  - Never repeat a colour (at most 6 categories plus "Autres").
  - Add a France bar when the categories match (GDP sectors, exports).

**Maps**
- **Locator:** an orthographic globe in the hero, 280 px, centred on the country centroid (drop rings with `cos c < 0`).
  - Sphere `--surface`, 30° graticule, land `--land`, the country in `--accent`.
  - Microstates get a 10 px ring.
- **Cities:** frame the country's bounding box plus 15 %.
  - Neighbours in `--land`, sea in `--surface`. The country in `--accent-soft` with a 1 px `--accent` outline.
  - Dots sized by √population; the capital is a ringed square.
  - Haloed labels placed by trying 8 candidate positions, with no leader lines. Second line ".8em 4,0 M".
  - 50 km scale bar.
  - Delete the city list and fix the comma bug.
- **Relief:** `max-height:560px; width:auto`, radius 4 px. Caption "Relief" plus the licence line required by CC BY-SA. At ≥ 1000 px, pair it with the cities map in one wide figure.

## 6. Sources (P0)

The markdown stays as it is. The parser turns `[S12, S13](#sources)` and `[S32 à S35](#sources)` into ids. JSON `source` strings gain `sources: [...]`.

**Marker:** one per paragraph or figure, at its end:
`<sup class="refs"><a href="#s12" id="c-12-a">12</a><a href="#s13" id="c-13-a">13</a></sup>`
- Inter .62em, `--muted`, opacity .75, no underline. Accent on hover or focus.
- Numbers separated by U+2009. Ranges shown as "32–35".
- Figures put the marker after the subtitle. Keyfacts put it after the label.

**List:**
- Intro "Sources consultées le 15 novembre 2026." Drop every per-item date.
- Numbered `ol` at .85rem/1.45, in 2 columns at ≥ 1000 px.
- Item: a hanging tabular number, the publisher in Inter 600, then the linked title in serif.
- Back-link chips `↩ Climat · Population`: one per citation, labelled with the short section name, pointing to `#c-12-a`, Inter .72rem accent.
- Moved figure notes appear under the item as muted italic "Note : …".
- `:target` highlights the item in `--accent-soft`.

## 7. Home (P1)

- Hero: the title plus "1 fiche sur 197" over a 3 px progress bar.
- **Fiche du jour** card: flag, name, chapô, read time and a small globe. The whole card is a link.
- **World map** (Equal Earth SVG): available countries are `<a>` paths in `--accent`, the rest are `--land`. No JS needed.
- Index tiles: `repeat(auto-fill,minmax(190px,1fr))`, each with a 20×15 flag (lipis/flag-icons, MIT), the name and the rank "01".
  - Available: `--ink`, a 3 px `--accent` left border and a "10 min" chip.
  - Upcoming: `--muted`, flag `grayscale(1) opacity(.5)`, and a single legend line instead of 196 "à venir".
- Sorting: keep palier and alpha, and add `?tri=continent` (new `ordre.csv` column). Alpha gets letter headings and an A–Z anchor bar.

## 8. Extras (P2)

- Reading progress with `animation-timeline: scroll()` inside `@supports`.
- `content-visibility:auto` on sections below the fold.
- A print stylesheet that prints URLs only in the source list.
- Re-shoot `shots/after/` with fixed mobile capture.
