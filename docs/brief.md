# Brief (2026-11-15)

## Product
- One fiche per country, 197 countries (193 UN members + Taiwan, Kosovo, Palestine, Vatican).
- About 10 minutes of reading, in French. Data-heavy: tables and charts over long prose.
- Server-rendered web app (not a static site), so accounts and reading progress can be added later.
  V1 is anonymous: a home page lists every country (selectable, visible); each fiche links back to it.
- Hosted on paulmondou.fr through home-paulmondou / infra-paulmondou. No notifications.
- Personal reader first, may be shared with friends.
- V2: accounts (email/password, same pattern as SommeilEnOr), fiches marked as read, progress on the home page.

## Fiche content (adapt to the country)
- Flag, world locator map. Relief map only when relief matters. Main cities.
- Charts: temperatures and rainfall by month, wages (median, mean), GDP by sector,
  age pyramid, languages, religions when mixed, one niche phenomenon when the country has one.
- Climate and seasons, way of life, wealth and inequality, resources and economy.
- History, culture and cuisine, religions, relations with France.
- Political regime, recent leaders, current dynamics: short background + last 20 years.
  When the defining upheaval is older, focus on it instead.
- Indices with sources (democracy, press freedom, corruption, HDI, Gini).

## Order
Arbitrary but reasoned: closeness to the reader's interests first (automotive engineering,
tech and semiconductors, sport, techno music, ties to France, current affairs), then the rest.
See `data/ordre.md` and `data/ordre.csv`.

## Production
- Generated in advance, in batches, spread over the cdx accounts.
- Pilot fiche first; launch the series once the format is validated.
- Sources: World Bank, IMF, open climate data, Natural Earth / OpenStreetMap, Wikipedia, press.

## Hosting and stack (decided 2026-11-15, revised)
- `pays.paulmondou.fr`: this repo builds its own Docker image; infra-paulmondou adds a Caddy block
  and a service (same pattern as SommeilEnOr). home-paulmondou only gets a link.
- Stack: Python 3.13, FastAPI, Jinja2 server-side templates, no frontend build. Charts and maps are
  SVG rendered server-side, no JavaScript needed to read a fiche. SQLite volume reserved for V2 accounts.
- Content lives in the repo as files (`fiches/<ISO3>/`), see `docs/format.md`. The app reads them.
- Public but not indexed (`noindex` meta + robots.txt).
- Pilot fiche: Taiwan.
- Generation accounts: claude, worka, workb (Codex runs have network).
