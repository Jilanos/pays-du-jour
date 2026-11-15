"""Regression checks for the reading contract, not just template snapshots."""

import json
import re
import shutil
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.format import euro, number, quantity, rounded, with_euro
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
        (1604000, "TWD", "1,6\u00a0million\u00a0TWD"),
        (1990000, "TWD", "2,0\u00a0millions\u00a0TWD"),
        (1.2e9, "USD", "1,2\u00a0milliard\u00a0USD"),
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
    # No France slot, reason or reference mark when the comparison is not comparable.
    for absent in ("Non comparable", "ndisponible", "comparison-note", "missing"):
        assert absent not in body
    energy = body.split('id="fact-energie-importee"', 1)[1].split("</section>", 1)[0]
    assert "France" not in energy and "metric-pair single" in energy
    gini = body.split('id="index-gini"', 1)[1].split('class="index-row"', 1)[0]
    assert "france-dot" not in gini and "index-france" not in gini
    wages = body.split('id="fig-salaires"', 1)[1].split("</figure>", 1)[0]
    assert "France" not in wages


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


def test_usa_figures_use_their_own_country_and_citations_roundtrip():
    with TestClient(create_app()) as client:
        response = client.get("/pays/USA")
    assert response.status_code == 200
    html = response.text
    body = html.split('<section class="sources"', 1)[0]
    assert 'class="legend-population">États-Unis</span>' in body
    assert "Taïwan" not in body
    assert "Relief de l’île" not in html
    links = Links(html)
    assert len(links.ids) == len(set(links.ids))
    assert all(href[1:] in links.ids for href in links.hrefs if href.startswith("#"))


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


def test_euro_conversion_uses_the_stored_rate_and_keeps_the_unit_suffix():
    fx = {"currency": "TWD", "per_euro": 35.217, "year": 2025}
    assert euro(50643, "TWD/mois", fx) == "1\u202f440\u00a0€/mois"
    assert with_euro("50 600 TWD", 1604000, "TWD", fx) == "50 600 TWD (≈\u00a045\u202f500\u00a0€)"
    with pytest.raises(ValueError, match="expects an amount in TWD"):
        euro(10, "USD", fx)


def test_production_wages_and_incomes_show_euros_with_a_cited_rate():
    with TestClient(create_app()) as client:
        html = client.get("/pays/TWN").text
    body, sources = html.split('<section class="sources"', 1)
    wages = body.split('id="fig-salaires"', 1)[1].split("</figure>", 1)[0]
    assert '50\u202f600\u00a0TWD/mois <span class="euro">(≈\u00a01\u202f440\u00a0€/mois)' in wages
    assert "1,6\u00a0million\u00a0TWD (≈\u00a045\u202f500\u00a0€)" in body
    assert "1\u00a0€ = 35,22\u00a0TWD, moyenne annuelle 2025" in sources
    assert 'href="#fig-salaires">↩' in sources.split('id="src-S57"', 1)[1].split("</li>", 1)[0]


def test_euro_conversion_rejects_a_rate_from_another_year(tmp_path):
    from dataclasses import replace

    from app.content import read_fiche

    folder = tmp_path / "TWN"
    shutil.copytree(ROOT / "fiches/TWN", folder)
    data = json.loads((folder / "data.json").read_text())
    data["euro"]["year"] = 2024
    (folder / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    with pytest.raises(ValueError, match="euro rate year 2024"):
        read_fiche("TWN", replace(Settings(), content_dir=tmp_path))


def test_china_chart_labels_and_relief_source_links_use_the_current_country():
    with TestClient(create_app()) as client:
        response = client.get("/pays/CHN")
    assert response.status_code == 200
    html = response.text
    assert '<span class="legend-population">Chine</span>' in html
    assert '<span class="legend-population">Taïwan</span>' not in html
    assert "<caption>Chine</caption>" in html
    assert "Relief de l’île" not in html
    links = Links(html)
    assert len(links.ids) == len(set(links.ids))
    assert all(href[1:] in links.ids for href in links.hrefs if href.startswith("#"))
