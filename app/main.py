"""Application factory and anonymous HTML routes. V2 routers can be registered here."""

import json
from collections import OrderedDict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import Settings
from .content import ISO3, alphabetical, country_list, read_fiche

APP_DIR = Path(__file__).resolve().parent


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Pays du jour", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    templates = Jinja2Templates(directory=APP_DIR / "templates")
    templates.env.globals["ui"] = json.loads((APP_DIR / "i18n/fr.json").read_text())
    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

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
    def home(request: Request, tri: str = "palier"):
        countries = country_list(settings)
        groups = OrderedDict()
        if tri == "alpha":
            groups["Tous les pays"] = sorted(countries, key=lambda c: alphabetical(c["pays"]))
        else:
            tri = "palier"
            for country in sorted(countries, key=lambda c: (int(c["palier"]), int(c["rang"]))):
                groups.setdefault(
                    f"Palier {country['palier']} · {country['palier_nom']}", []
                ).append(country)
        return templates.TemplateResponse(
            request=request,
            name="home.html",
            context={
                "groups": groups,
                "tri": tri,
                "total": len(countries),
                "available": sum(c["available"] for c in countries),
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
        return templates.TemplateResponse(
            request=request, name="fiche.html", context={"fiche": content}
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
