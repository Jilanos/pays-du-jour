import json
import re
from copy import deepcopy
from math import dist
from xml.etree import ElementTree as ET

import pytest

from app.config import Settings
from app.content import read_fiche
from app.maps import cities, map_point, path, validate_city_map

CODES = ("TWN", "USA", "CHN", "CHE", "MAR", "DZA", "JPN", "UKR", "RUS")


def country_data(code):
    return json.loads((Settings().content_dir / code / "data.json").read_text())


def svg_root(rendered):
    return ET.fromstring(rendered[rendered.index("<svg") : rendered.rindex("</svg>") + 6])


@pytest.mark.parametrize("filename", ("countries-50m.json", "world-110m.json"))
def test_ukraine_locator_includes_crimea_without_duplicate_russian_highlight(filename):
    features = json.loads((Settings().geo_dir / filename).read_text())

    def contains(geometry, point):
        polygons = (
            geometry["coordinates"]
            if geometry["type"] == "MultiPolygon"
            else [geometry["coordinates"]]
        )

        def in_ring(ring):
            x, y = point
            inside = False
            for (ax, ay), (bx, by) in zip(ring, ring[1:], strict=False):
                if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                    inside = not inside
            return inside

        return any(in_ring(p[0]) and not any(in_ring(h) for h in p[1:]) for p in polygons)

    # Inland reference points in Crimea and each country's undisputed mainland.
    for point in ((34.1, 44.95), (33.6, 44.65), (30.52, 50.45)):
        assert contains(features["UKR"], point)
        assert not contains(features["RUS"], point)
    assert contains(features["RUS"], (37.62, 55.75))
    assert not contains(features["UKR"], (37.62, 55.75))


def test_distant_polygon_crossing_opposite_meridian_stays_outside_regional_frame():
    geometry = {
        "type": "Polygon",
        "coordinates": [[[-80, 45], [-60, 45], [-60, 50], [-80, 50], [-80, 45]]],
    }
    rendered = path(geometry, lambda p: (200 + (p[0] - 107) * 6, p[1]), 107)
    for ring in rendered.split("M")[1:]:
        xs = [float(x) for x in re.findall(r"(-?[\d.]+),-?[\d.]+", ring)]
        assert max(xs) < 0 or min(xs) > 400


@pytest.mark.parametrize(
    "point,expected",
    [
        ((139.6917, 35.6895), (0.5445411317, 0.6420770202)),
        ((141.3545, 43.0621), (0.6236091298, 0.1766351010)),
        ((127.6809, 26.2124), (0.8210804379, 0.8419204043)),
        ((128.24, 45.86), (0, 0)),
        ((131.44, 23.71), (1, 1)),
        ((128, 30.90), (0.8362684436, 0.5457991156)),
    ],
)
def test_japan_module_reference_locations(point, expected):
    # Coastal cities, Naha in the side panel, frame corners and the branch boundary.
    data = {"projection": {"type": "japan_side_map"}}
    assert map_point(data, point) == pytest.approx(expected, abs=1e-8)


def test_japan_projection_rejects_wrong_module_and_rectangular_bounds():
    data = deepcopy(country_data("MAR")["cities_map"])
    data["projection"] = {"type": "japan_side_map"}
    with pytest.raises(ValueError, match="exact Wikipedia module"):
        validate_city_map(data, Settings().content_dir / "MAR/assets")
    data["definition_url"] = "https://en.wikipedia.org/wiki/Module:Location_map/data/Japan"
    with pytest.raises(ValueError, match="two frames"):
        validate_city_map(data, Settings().content_dir / "MAR/assets")


def test_rectangular_map_corners_and_antimeridian():
    data = {
        "projection": {"type": "equirectangular"},
        "bounds": {"left": 170, "right": -170, "top": 20, "bottom": -10},
    }
    assert map_point(data, (170, 20)) == (0, 0)
    assert map_point(data, (-170, -10)) == (1, 1)
    assert map_point(data, (180, 5)) == (0.5, 0.5)


@pytest.mark.parametrize(
    "point,expected",
    [
        ((-3.7038, 40.4168), (0.4215102041, 0.4106391753)),
        ((2.1734, 41.3851), (0.8213197279, 0.3108144330)),
        ((-15.4138, 28.0997), (0.8387030965, 0.9346074766)),
        ((-9.9, 44.4), (0, 0)),
        ((4.8, 34.7), (1, 1)),
        ((-26.925, 38.1), (0, 0)),
        ((-13.2, 27.4), (1, 1)),
        ((-10, 40), (-0.0068027211, 0.4536082474)),
    ],
)
def test_spain_module_reference_locations(point, expected):
    # Madrid, Barcelona, Las Palmas, both frame corners and the longitude boundary.
    data = {"projection": {"type": "spain_side_map"}}
    assert map_point(data, point) == pytest.approx(expected, abs=1e-8)


def test_spain_projection_rejects_wrong_module_and_rectangular_bounds():
    data = deepcopy(country_data("MAR")["cities_map"])
    data["projection"] = {"type": "spain_side_map"}
    with pytest.raises(ValueError, match="exact Wikipedia module"):
        validate_city_map(data, Settings().content_dir / "MAR/assets")
    data["definition_url"] = "https://en.wikipedia.org/wiki/Module:Location_map/data/Spain"
    with pytest.raises(ValueError, match="two frames"):
        validate_city_map(data, Settings().content_dir / "MAR/assets")


@pytest.mark.parametrize(
    "code,point,expected",
    [
        ("USA", (-77.04, 38.89), (0.81631028, 0.43527750)),
        ("USA", (-122.33, 47.61), (0.11490606, 0.09482243)),
        ("CHN", (116.39, 39.91), (0.69260357, 0.42323668)),
        ("CHN", (121.5, 31.2), (0.80296350, 0.62750885)),
        # Russia module formulas evaluated literally: Moscow, Vladivostok, Yakutsk, Kaliningrad.
        ("RUS", (37.613577, 55.75411), (0.13501950, 0.44061778)),
        ("RUS", (131.910026, 43.130015), (0.80590512, 0.87978916)),
        ("RUS", (129.735016, 62.034959), (0.68425201, 0.51616869)),
        ("RUS", (20.51, 54.71), (0.05567427, 0.27586892)),
    ],
)
def test_module_reference_locations(code, point, expected):
    # Reference points from the module examples, expressed as fractions of the full image.
    assert map_point(country_data(code)["cities_map"], point) == pytest.approx(expected, abs=1e-7)


@pytest.mark.parametrize("code", CODES)
def test_licensed_assets_pins_insets_and_sources(code):
    data = country_data(code)
    map_data = data["cities_map"]
    validate_city_map(map_data, Settings().content_dir / code / "assets")
    assert "CC BY-SA" in map_data["credit"]["license"]
    rendered = cities(code, code, data["cities"], map_data, inset=data.get("cities_inset"))
    root = svg_root(rendered)
    images = root.findall(".//{*}image")
    assert len(images) == (2 if data.get("cities_inset") else 1)
    assert all(im.get("href") == f"/pays/{code}/assets/{map_data['file']}" for im in images)
    assert not root.findall(".//{*}path")  # No country outline redrawn from geometry.
    pins = root.findall(".//{*}g[@class='city-pin']")
    assert len(pins) == len(data["cities"])
    image_h = 244 * map_data["height"] / map_data["width"]
    for city in data["cities"]:
        pin = next(p for p in pins if p.get("data-city") == city["name"])
        u, v = map_point(map_data, (city["lon"], city["lat"]))
        assert float(pin.get("data-origin-x")) == pytest.approx(8 + u * 244)
        assert float(pin.get("data-origin-y")) == pytest.approx(8 + v * image_h)
    # Pins in each frame must be separate, including dense clusters.
    inset = root.find("{*}svg")
    frames = [root, inset] if inset is not None else [root]
    for frame in frames:
        dots = frame.findall("./{*}g[@class='city-pin']/{*}circle")
        points = [(float(p.get("cx")), float(p.get("cy"))) for p in dots]
        _, _, width, height = map(float, frame.get("viewBox").split())
        assert all(11 <= x <= width - 11 and 11 <= y <= height - 11 for x, y in points)
        assert all(dist(a, b) >= 22 for i, a in enumerate(points) for b in points[i + 1 :])
    if inset is not None:
        assert float(inset.get("y")) >= 8 + image_h
    html = str(read_fiche(code, Settings()).html)
    assert 'id="src-CITYMAP"' in html
    assert map_data["credit"]["author"] in html
    assert map_data["credit"]["license_url"] in html
    assert 'href="#villes"' in html


@pytest.mark.parametrize(
    "change,match",
    [
        ({"file": "../cities.svg"}, "local SVG"),
        ({"file": "missing.svg"}, "Missing city map"),
        ({"width": 0}, "positive"),
        ({"credit": {}}, "credit needs"),
        ({"source_ids": []}, "source_ids"),
        ({"projection": {"type": "mercator"}}, "Unsupported"),
        ({"bounds": {"left": 0, "right": 5, "top": 30, "bottom": 30}}, "bottom < top"),
    ],
)
def test_invalid_map_contract_fails(change, match):
    data = deepcopy(country_data("MAR")["cities_map"])
    data.update(change)
    with pytest.raises(ValueError, match=match):
        validate_city_map(data, Settings().content_dir / "MAR/assets")


def test_large_asset_fails(tmp_path):
    data = country_data("MAR")["cities_map"]
    (tmp_path / data["file"]).write_bytes(b"x" * 400_001)
    with pytest.raises(ValueError, match="400 KB"):
        validate_city_map(data, tmp_path)


def test_city_outside_map_and_clipped_inset_fail():
    data = country_data("TWN")
    wrong = [{"name": "Outside", "population": 1, "lon": 100, "lat": 25}]
    with pytest.raises(ValueError, match="outside licensed map"):
        cities("TWN", "Taiwan", wrong, data["cities_map"])
    inset = {**data["cities_inset"], "zoom": 100}
    with pytest.raises(ValueError, match="clipped in inset"):
        cities("TWN", "Taiwan", data["cities"], data["cities_map"], inset=inset)
