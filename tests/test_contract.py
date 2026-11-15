"""Regression checks for the reading contract, not just template snapshots."""

import json
import re
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.format import number, quantity, rounded
from app.main import create_app
from app.sources import Sources


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids, self.hrefs = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (4044831, "habitants", "4,0\u00a0millions\u00a0d’habitants"),
        (36197.3371, "km²", "36\u202f200\u00a0km²"),
        (922454000000, "USD", "922\u00a0milliards\u00a0USD"),
        (20.79, "%", "20,8\u202f%"),
        (0, "%", "0\u202f%"),
    ],
)
def test_french_reading_precision(value, unit, expected):
    assert quantity(value, unit) == expected


def test_index_precision_and_invalid_numbers():
    assert number(0.92, 3, fixed=True) == "0,920"
    assert rounded(0.695, 1) == "0,7"
    with pytest.raises(ValueError):
        number(float("inf"))


def test_production_fiche_has_unique_figures_and_complete_source_roundtrips():
    with TestClient(create_app()) as client:
        html = client.get("/pays/TWN").text
    links = Links(html)
    assert len(links.ids) == len(set(links.ids))
    assert all(href[1:] in links.ids for href in links.hrefs if href.startswith("#"))
    assert html.count("<h1>") == 1
    body, sources = html.split('<section class="sources"', 1)
    assert not re.search(r'\[S\d|<a[^>]+href="https?://', body)
    assert "Consultées le 15 novembre 2026" in sources
    data = json.loads((ROOT / "fiches/TWN/data.json").read_text())
    for chart in data["charts"]:
        assert body.count(f'id="fig-{chart["id"]}"') == 1
    assert body.count('class="indices"') == 1
    assert "4,0\u00a0millions\u00a0d’habitants" in body
    assert "4\u202f044\u202f831" not in body
    assert "Non comparable" in body and "indisponible" in body


def test_bibliography_numbers_follow_display_order_not_citation_order():
    sources = Sources([{"id": k, "text": k} for k in ["A", "B", "C"]], "2026-11-15")
    sources.cite("first", "Premier", ["C", "A"])
    sources.cite("second", "Second", ["B", "C"])
    html = sources.render()
    assert 'href="#src-A">1</a>' in html
    assert 'href="#src-C">3</a>' in html
    assert 'href="#first">↩ Premier' in html
    with pytest.raises(ValueError, match="Unknown source"):
        sources.cite("missing", "Absent", ["Z"])


def test_every_country_has_local_flag_and_continent():
    from app.content import country_list

    countries = country_list(Settings())
    assert len(countries) == 197
    for country in countries:
        assert (ROOT / f"app/static/flags/{country['iso2'].lower()}.svg").is_file()
        assert country["continent"]


def test_home_search_filters_and_noninteractive_forthcoming_countries(client):
    for query in ("/?q=france", "/?disponibles=1"):
        html = client.get(query).text
        assert re.findall(r'data-iso3="([A-Z]{3})"', html) == ["FRA"]
    html = client.get("/?q=etats&tri=continent").text
    assert "États-Unis" in html and "Amérique du Nord" in html
    assert 'href="/pays/USA"' not in html
    assert 'name="q" value="etats"' in html
    assert "data-iso3=" not in client.get("/?q=introuvable").text


def test_reference_pyramid_cohorts_and_total():
    ref = json.loads((ROOT / "data/reference/FRA.json").read_text())
    data = json.loads((ROOT / "fiches/TWN/data.json").read_text())
    pyramid = next(c for c in data["charts"] if c["type"] == "pyramid")
    assert pyramid["age_groups"] == ref["pyramide-france"]["age_groups"]
    assert (
        sum(ref["pyramide-france"]["male"] + ref["pyramide-france"]["female"])
        == ref["population"]["value"]
    )
    for item in data["keyfacts"] + data["indices"] + data["charts"]:
        comparison = ref[item["france"]]
        assert comparison["status"] in ("comparable", "non_comparable", "unavailable")
        if comparison["status"] != "comparable":
            assert comparison["reason"]
            assert "value" not in comparison and "values" not in comparison
