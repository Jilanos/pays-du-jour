from copy import deepcopy
from xml.etree import ElementTree as ET

import pytest

from app.charts import RENDERERS, render_chart


@pytest.mark.parametrize("kind", RENDERERS)
def test_each_chart_has_accessible_plot_and_exact_data_without_source_caption(charts, kind):
    chart = next(c for c in charts if c["type"] == kind)
    rendered = render_chart(chart)
    if kind in ("bar", "barh", "share"):
        assert "<svg" not in rendered
        assert all(label in rendered for label in chart["labels"])
    else:
        start, end = rendered.index("<svg"), rendered.index("</svg>") + 6
        root = ET.fromstring(rendered[start:end])
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.attrib["role"] == "img"
        assert root.find("{*}title").text == chart["title"]
    assert "Source :" not in rendered
    assert chart["note"] not in rendered
    assert "Voir les données" in rendered
    assert (chart.get("unit") or "°C") in rendered
    assert "nan" not in rendered.lower()
    assert "infinity" not in rendered.lower()


@pytest.mark.parametrize("kind", RENDERERS)
def test_zero_values_render_without_division_by_zero(charts, kind):
    chart = deepcopy(next(c for c in charts if c["type"] == kind))
    if kind == "share":
        chart["values"] = [0, 100]
    else:
        for key in ("tmin", "tmax", "precip_mm", "male", "female", "values"):
            if key in chart:
                chart[key] = [0] * len(chart[key])
        for series in chart.get("series", []):
            series["values"] = [0] * len(series["values"])
    ET.fromstring("<root>" + RENDERERS[kind](chart) + "</root>")


def test_rejects_mismatched_or_nonfinite_data(charts):
    chart = deepcopy(next(c for c in charts if c["type"] == "bar"))
    chart["values"] = [1]
    with pytest.raises(ValueError, match="equal lengths"):
        render_chart(chart)
    chart["values"] = [float("nan"), 2]
    with pytest.raises(ValueError, match="finite"):
        render_chart(chart)


def test_line_keeps_real_time_gaps_and_separates_nearby_end_labels():
    from app.charts import line

    chart = {
        "id": "time",
        "type": "line",
        "title": "Time",
        "unit": "points",
        "year": 2026,
        "x": [2000, 2001, 2010, 2025],
        "series": [{"name": f"Série {i}", "values": [10, None, 5, i]} for i in range(4)],
    }
    root = ET.fromstring(line(chart, mobile=True))
    assert len(root.findall("{*}polyline")) == 8
    positions = [
        float(n.attrib["y"])
        for n in root.findall("{*}text")
        if n.attrib.get("class") == "value-label"
    ]
    assert all(b - a >= 34 for a, b in zip(positions, positions[1:], strict=False))
    chart["_france"] = {"values": [1, 2, 3, 4]}
    with pytest.raises(ValueError, match="four series"):
        line(chart)


def test_many_periods_use_stacked_areas_with_a_separate_france_column():
    from app.charts import stacked

    chart = {
        "title": "Sectors",
        "labels": [str(y) for y in range(2020, 2026)],
        "unit": "%",
        "series": [{"name": "A", "values": [40] * 6}, {"name": "B", "values": [60] * 6}],
        "_france": {"values": [25, 75]},
    }
    root = ET.fromstring(stacked(chart, mobile=True))
    areas = root.findall("{*}polygon")
    bars = root.findall("{*}rect")
    assert len(areas) == len(bars) == 2
    assert all(n.attrib["stroke"] == "var(--france)" for n in bars)
    area_right = max(float(point.split(",")[0]) for point in areas[0].attrib["points"].split())
    assert float(bars[0].attrib["x"]) - area_right >= 24
