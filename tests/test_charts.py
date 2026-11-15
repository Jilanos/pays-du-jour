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
