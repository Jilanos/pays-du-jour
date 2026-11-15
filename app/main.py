"""Application factory and anonymous HTML routes. V2 routers can be registered here."""

import json
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import Settings
from .content import ISO3, alphabetical, country_list, read_fiche
from .format import date_fr
from .maps import locator

APP_DIR = Path(__file__).resolve().parent


class HeadAsGet:
    """Answer HEAD like GET without a body: FastAPI GET routes otherwise return 405."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "HEAD":
            await self.app(scope, receive, send)
            return

        async def send_without_body(message):
            if message["type"] == "http.response.body":
                if message.get("more_body"):
                    return
                message = {"type": "http.response.body", "body": b"", "more_body": False}
            await send(message)

        await self.app({**scope, "method": "GET"}, receive, send_without_body)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Pays du jour", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    templates = Jinja2Templates(directory=APP_DIR / "templates")
    templates.env.filters["date_fr"] = date_fr
    templates.env.globals["ui"] = json.loads((APP_DIR / "i18n/fr.json").read_text())
    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    app.add_middleware(HeadAsGet)

    @app.middleware("http")
    async def noindex(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"status": exc.status_code},
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request, tri: str = "palier", q: str = "", disponibles: str = ""):
        countries = country_list(settings)
        available = [c for c in countries if c["available"]]
        featured = read_fiche(available[0]["iso3"], settings) if available else None
        selected = [
            c
            for c in countries
            if (not disponibles or c["available"])
            and alphabetical(q.strip()) in alphabetical(c["pays"])
        ]
        groups = OrderedDict()
        if tri == "alpha":
            for country in sorted(selected, key=lambda c: alphabetical(c["pays"])):
                groups.setdefault(alphabetical(country["pays"])[0].upper(), []).append(country)
        elif tri == "continent":
            for country in sorted(
                selected, key=lambda c: (c.get("continent", ""), alphabetical(c["pays"]))
            ):
                groups.setdefault(country.get("continent", "Autres"), []).append(country)
        else:
            tri = "palier"
            for country in sorted(selected, key=lambda c: (int(c["palier"]), int(c["rang"]))):
                groups.setdefault(country["palier_nom"], []).append(country)
        queries = {
            mode: urlencode({"tri": mode, "q": q, **({"disponibles": "1"} if disponibles else {})})
            for mode in ("palier", "alpha", "continent")
        }
        return templates.TemplateResponse(
            request=request,
            name="home.html",
            context={
                "groups": groups,
                "tri": tri,
                "total": len(countries),
                "available": len(available),
                "featured": featured,
                "featured_map": Markup(
                    locator(featured.meta["iso3"], featured.meta["nom"], settings.geo_dir)
                )
                if featured
                else "",
                "q": q,
                "only_available": bool(disponibles),
                "result_count": len(selected),
                "sort_queries": queries,
            },
        )

    @app.get("/pays/{iso3}", response_class=HTMLResponse)
    def fiche(request: Request, iso3: str):
        code = iso3.upper()
        if not ISO3.fullmatch(code) or code not in {c["iso3"] for c in country_list(settings)}:
            raise HTTPException(404)
        try:
            content = read_fiche(code, settings)
        except FileNotFoundError:
            raise HTTPException(404) from None
        countries = country_list(settings)
        available = [c for c in countries if c["available"]]
        position = next(i for i, c in enumerate(available) if c["iso3"] == code)
        next_country = available[(position + 1) % len(available)] if len(available) > 1 else None
        return templates.TemplateResponse(
            request=request,
            name="fiche.html",
            context={"fiche": content, "next_country": next_country, "total": len(countries)},
        )

    @app.get("/pays/{iso3}/assets/{filename}")
    def asset(iso3: str, filename: str):
        code = iso3.upper()
        if (
            not ISO3.fullmatch(code)
            or filename != Path(filename).name
            or Path(filename).suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}
        ):
            raise HTTPException(404)
        base = (settings.content_dir / code / "assets").resolve()
        path = (base / filename).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path)

    @app.get("/healthz")
    def health():
        return {"status": "ok"}

    @app.get("/robots.txt", response_class=PlainTextResponse)
    def robots():
        return "User-agent: *\nDisallow: /\n"

    return app
