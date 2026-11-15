import json
import re
import shutil
from dataclasses import replace
from xml.etree import ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.content import alphabetical, country_list, read_fiche
from app.main import create_app
from app.maps import cities, locator


def test_home_lists_all_countries_and_available_fiche(client):
    response = client.get("/")
    assert response.status_code == 200
    codes = re.findall(r'data-iso3="([A-Z]{3})"', response.text)
    assert len(codes) == len(set(codes)) == 197
    assert 'href="/pays/FRA"' in response.text
    assert 'href="/pays/TWN"' not in response.text
    assert "à venir" not in response.text
    assert "Par affinités" in response.text and "Tour du monde" in response.text


def test_alpha_toggle_is_french_alphabetical(client, settings):
    response = client.get("/?tri=alpha")
    codes = re.findall(r'data-iso3="([A-Z]{3})"', response.text)
    expected = sorted(country_list(settings), key=lambda c: alphabetical(c["pays"]))
    assert codes == [c["iso3"] for c in expected]
    assert 'aria-current="page">Ordre alphabétique' in response.text


def test_fixture_resolves_every_placeholder_and_builds_toc(client):
    response = client.get("/pays/FRA")
    assert response.status_code == 200
    assert "{{" not in response.text
    assert response.text.count('class="graphic"') == 7  # HTML rows and responsive SVGs.
    assert 'href="#population"' in response.text
    assert 'id="population"' in response.text
    assert "← tous les pays" in response.text
    assert "Source de test" in response.text and "Lire les indices" in response.text
    assert "/pays/FRA/assets/flag.svg" in response.text
    assert "/pays/FRA/assets/relief.svg" in response.text
    assert "<table>" in response.text
    # The chapter sidebar folds without JavaScript and starts open.
    assert '<details class="toc-panel" open><summary>' in response.text
    assert client.get("/pays/fra").status_code == 200


@pytest.mark.parametrize(
    "url",
    [
        "/pays/ZZZ",
        "/pays/TWN",
        "/pays/not-a-code",
        "/missing",
        "/pays/FRA/assets/missing.svg",
        "/pays/FRA/assets/data.json",
    ],
)
def test_unknown_country_or_file_returns_html_404(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert '<meta name="robots" content="noindex">' in response.text


@pytest.mark.parametrize("url", ["/", "/?tri=alpha", "/pays/FRA"])
def test_pages_are_noindex_without_scripts(client, url):
    response = client.get(url)
    assert '<meta name="robots" content="noindex">' in response.text
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert "<script" not in response.text


def test_health_robots_and_assets(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/robots.txt").text == "User-agent: *\nDisallow: /\n"
    assert (
        client.get("/pays/FRA/assets/flag.svg").headers["content-type"].startswith("image/svg+xml")
    )
    assert client.get("/static/style.css").status_code == 200


def test_relief_is_conditional(settings, tmp_path):
    shutil.copytree(settings.content_dir, tmp_path / "fiches")
    config = replace(settings, content_dir=tmp_path / "fiches")
    fiche = config.content_dir / "FRA/fiche.md"
    fiche.write_text(fiche.read_text().replace("relief_pertinent: true", "relief_pertinent: false"))
    assert "assets/relief" not in read_fiche("FRA", config).html
    fiche.write_text(fiche.read_text().replace("relief_pertinent: false", "relief_pertinent: true"))
    (config.content_dir / "FRA/assets/relief.svg").unlink()
    assert "{{" not in read_fiche("FRA", config).html
    assert "assets/relief" not in read_fiche("FRA", config).html


def test_settings_and_factory_do_not_open_v2_database(monkeypatch, tmp_path):
    path = tmp_path / "unused.sqlite3"
    monkeypatch.setenv("PAYS_DB_PATH", str(path))
    settings = Settings()
    assert settings.database_path == path
    with TestClient(create_app(settings)) as client:
        assert client.get("/").status_code == 200
    assert not path.exists()


def test_geo_extract_covers_all_197_countries_and_stays_small(settings):
    countries = json.loads((settings.geo_dir / "countries-50m.json").read_text())
    assert {c["iso3"] for c in country_list(settings)} == countries.keys()
    assert sum(p.stat().st_size for p in settings.geo_dir.glob("*.json")) < 5_000_000
    # Tiny countries absent from 110m still have a highlighted locator marker.
    assert 'class="locator-dot"' in locator("VAT", "Vatican", settings.geo_dir)
    for code in ("FJI", "KIR", "RUS", "FRA", "VAT", "TWN", "XKX", "PSE"):
        rendered = cities(code, code, [], settings.geo_dir)
        start, end = rendered.index("<svg"), rendered.index("</svg>") + 6
        ET.fromstring(rendered[start:end])


def test_adjacent_placeholder_lines_resolve_but_code_examples_remain_literal(settings, tmp_path):
    shutil.copytree(settings.content_dir, tmp_path / "fiches")
    config = replace(settings, content_dir=tmp_path / "fiches")
    path = config.content_dir / "FRA/fiche.md"
    path.write_text(
        path.read_text() + "\n## Blocs adjacents\nTexte avant\n"
        "{{chart:adjacent}}\n{{chart:second}}\nTexte après\n"
        "\n```text\n{{chart:salaires}}\n```\n"
        "\n    {{map:cities}}\n"
    )
    data_path = config.content_dir / "FRA/data.json"
    data = json.loads(data_path.read_text())
    original = next(c for c in data["charts"] if c["id"] == "salaires")
    data["charts"] += [{**original, "id": name} for name in ("adjacent", "second")]
    data_path.write_text(json.dumps(data))
    html = read_fiche("FRA", config).html
    assert html.count('class="graphic"') == 9
    assert "<p>Texte avant</p>" in html and "<p>Texte après</p>" in html
    assert '<code class="language-text">{{chart:salaires}}' in html
    assert "<code>{{map:cities}}" in html


@pytest.mark.parametrize("url", ["/", "/pays/FRA", "/robots.txt", "/static/style.css"])
def test_head_answers_like_get_without_body(client, url):
    get = client.get(url)
    head = client.head(url)
    assert head.status_code == get.status_code == 200
    assert head.headers["content-type"] == get.headers["content-type"]
    assert head.headers["x-robots-tag"] == "noindex, nofollow"
    assert head.content == b""


def test_head_unknown_country_is_404(client):
    assert client.head("/pays/XXX").status_code == 404
