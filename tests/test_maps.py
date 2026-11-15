import re
from xml.etree import ElementTree as ET

import pytest

from app.config import Settings
from app.maps import cities, path


def test_distant_polygon_crossing_opposite_meridian_stays_outside_regional_frame():
    geometry = {
        "type": "Polygon",
        "coordinates": [[[-80, 45], [-60, 45], [-60, 50], [-80, 50], [-80, 45]]],
    }
    rendered = path(geometry, lambda p: (200 + (p[0] - 107) * 6, p[1]), 107)
    for ring in rendered.split("M")[1:]:
        xs = [float(x) for x in re.findall(r"(-?[\d.]+),-?[\d.]+", ring)]
        assert max(xs) < 0 or min(xs) > 400


@pytest.mark.parametrize("code", ["CHN", "TWN", "VAT"])
def test_city_scale_stays_visible_at_continental_island_and_microstate_sizes(code):
    rendered = cities(code, code, [], Settings().geo_dir)
    start, end = rendered.index("<svg"), rendered.index("</svg>") + 6
    root = ET.fromstring(rendered[start:end])
    scale = next(p for p in root.findall(".//{*}path") if p.attrib["d"].startswith("M18 326"))
    width = float(re.search(r" h([\d.]+)", scale.attrib["d"]).group(1))
    assert 30 <= width <= 80


def test_data_driven_inset_moves_grouped_cities_out_of_the_main_map():
    city_data = [
        {"name": "A", "population": 1, "lat": 33.6, "lon": -7.6},
        {"name": "B", "population": 1, "lat": 34.0, "lon": -6.8},
        {"name": "C", "population": 1, "lat": 31.6, "lon": -8.0},
    ]
    inset = {
        "label": "Nord",
        "cities": ["A", "B"],
        "lon": -7.7,
        "lat": 33.3,
        "scale": 38,
        "x": 140,
        "y": 192,
        "width": 114,
        "height": 86,
    }
    rendered = cities("MAR", "Maroc", city_data, Settings().geo_dir, inset=inset, note="Note")
    start, end = rendered.index("<svg"), rendered.rindex("</svg>") + 6
    root = ET.fromstring(rendered[start:end])
    frame = next(s for s in root.iter("{http://www.w3.org/2000/svg}svg") if s is not root)
    inner = frame.findall(".//{*}circle")
    outer = [c for c in root.findall(".//{*}circle") if c not in inner]
    assert len(inner) == 2 and len(outer) == 1
    assert '<p class="figure-note">Note</p>' in rendered
