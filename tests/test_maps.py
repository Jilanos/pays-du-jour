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
