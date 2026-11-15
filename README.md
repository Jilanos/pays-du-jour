# Pays du jour

A French country reader: 197 countries, short fiches, server-rendered charts and
maps. Python 3.13, FastAPI, Jinja2 and markdown-it-py. No frontend build or JavaScript.

## Run locally

Install [uv](https://docs.astral.sh/uv/), then:

```sh
uv sync --frozen
uv run uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Countries with `fiches/<ISO3>/fiche.md` are linked;
others display “à venir”. Choose “Ordre alphabétique” to switch from the reading
order grouped by palier. A fiche is served at `/pays/<ISO3>`.

Preview the test fiche without adding any production content:

```sh
PAYS_CONTENT_DIR=tests/fixtures/fiches uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/pays/FRA. This fixture uses **fictional test data** and
contains all seven chart types, both vector maps, a relief illustration and a flag.
Stop the first server before starting another on the same port.

## Docker

```sh
docker build -t pays-du-jour .
docker run --rm --name pays-du-jour -p 127.0.0.1:8000:8000 pays-du-jour
```

The container runs as UID 10001 on port 8000 and checks `/healthz`. It installs only
locked runtime dependencies. Country content and compact Natural Earth geometry
are included in the image; no download occurs at startup. Rebuild after adding
fiches. To preview the fixture with Docker instead:

```sh
docker run --rm -p 127.0.0.1:8000:8000 \
  -v "$PWD/tests/fixtures/fiches:/preview:ro" \
  -e PAYS_CONTENT_DIR=/preview pays-du-jour
```

## Content and configuration

See [the content contract](docs/format.md) and [the section template](templates/fiche.md).
A fiche folder contains `fiche.md` with YAML front matter, `data.json`, and `assets/`.
Placeholders occupy their own line: `{{keyfacts}}`, `{{chart:id}}`,
`{{map:locator}}`, `{{map:cities}}`, `{{map:relief}}`. Charts include a source line
and expandable data table. The key facts block also renders `indices`.

The app displays `assets/flag.svg` when present. Relief appears only when
`relief_pertinent` is true and an `assets/relief.jpg`, `.jpeg`, `.png`, `.webp` or
`.svg` exists. Credits belong in the fiche’s Sources section. Markdown raw HTML is
disabled; tables and heading anchors are supported. Treat committed SVG assets as
trusted content. Missing chart data is a content error to fix before publication.

Environment variables are read by the application factory:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAYS_CONTENT_DIR` | Repo `fiches/` | Fiche folders; relative values use the working directory |
| `PAYS_ORDER_PATH` | Repo `data/ordre.csv` | Country list and reading order |
| `PAYS_GEO_DIR` | Repo `data/geo/` | Committed map geometry |
| `PAYS_DB_PATH` | `/data/pays.sqlite3` | Reserved for V2; unused in V1 |

`app/main.py` owns the factory and route composition. `app/content.py` reads fiches,
`app/charts.py` renders SVG, and `app/maps.py` draws maps. The
[V2 extension notes](app/future/README.md) identify where auth and `fiches_lues`
will fit. V1 creates no database and has no account routes.

All HTML pages carry `noindex`; `/robots.txt` disallows crawling. Responses also
carry `X-Robots-Tag: noindex, nofollow`. These are crawler directives; fiches remain
publicly accessible.

## Validate

```sh
uv run pytest
uv run ruff check app tests scripts
uv run ruff format --check app tests scripts
```

Tests cover SVG rendering, zero and negative values, the 197-country list, sorting,
placeholder resolution, map coverage, optional relief, assets, 404s, crawler rules
and the unused V2 database setting. A browser smoke check can use Playwright from
the development dependencies:

```sh
uv run playwright install chromium
# With the fixture server running on port 8001:
uv run python scripts/check_browser.py http://127.0.0.1:8001
```

This checks both themes at 375px and 1440px with JavaScript disabled, including
expanded chart data tables. Screenshots go to `/tmp/pays-du-jour-preview/`.

Map provenance and regeneration: [data/geo/README.md](data/geo/README.md).
