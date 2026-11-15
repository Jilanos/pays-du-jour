"""Regional locators and numbered city maps from local Natural Earth geometry."""

import json
from functools import lru_cache
from html import escape
from math import cos, radians
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

from .charts import el, finish, text
from .format import quantity


@lru_cache(maxsize=8)
def load_geo(directory: Path, name: str):
    return json.loads((directory / name).read_text())


def rings(geometry):
    polygons = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        polygons = [polygons]
    return [ring for polygon in polygons for ring in polygon]


def path(geometry, project):
    return " ".join(
        "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in map(project, ring)) + " Z"
        for ring in rings(geometry)
    )


def main_bounds(geometry):
    polygons = (
        geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    )

    def area(p):
        return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p[0], p[0][1:], strict=False)))

    largest = max(area(p) for p in polygons)
    pts = [p for polygon in polygons if area(polygon) >= largest * 0.25 for p in polygon[0]]
    # Shortest interval around the antimeridian.
    lons = sorted(p[0] % 360 for p in pts)
    _, idx = max(
        (lons[(i + 1) % len(lons)] + (360 if i == len(lons) - 1 else 0) - v, i)
        for i, v in enumerate(lons)
    )
    start = lons[(idx + 1) % len(lons)]

    def wrap(lon):
        return (lon % 360 - start) % 360

    return start, max(wrap(p[0]) for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)


def contiguous_usa(geometry):
    """Keep the mainland for a readable regional view of the selected cities."""
    return {
        "type": "MultiPolygon",
        "coordinates": [
            polygon
            for polygon in geometry["coordinates"]
            if all(-126 < lon < -66 and 24 < lat < 50 for lon, lat in polygon[0])
        ],
    }


def canvas(title, width, height):
    root = Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {width} {height}",
            "role": "img",
            "class": "map",
        },
    )
    SubElement(root, "title").text = title
    return root


def locator(iso3, name, geo_dir, marker=""):
    world = load_geo(geo_dir, "world-110m.json")
    country = load_geo(geo_dir, "countries-50m.json")[iso3]
    if iso3 == "USA":
        country = contiguous_usa(country)
    start, dx, lo, hi = main_bounds(country)
    lon = (start + dx / 2 + 180) % 360 - 180
    lat = (lo + hi) / 2
    root = canvas(f"Situation de {name} : vue régionale et repère mondial", 400, 320)
    defs = el(root, "defs")
    clip = el(defs, "clipPath", id=f"locator-frame-{iso3}")
    el(clip, "rect", width=400, height=320, rx=8)
    group = el(root, "g", clip_path=f"url(#locator-frame-{iso3})")
    el(group, "rect", width=400, height=320, fill="var(--map-sea)")
    factor = max(0.25, cos(radians(lat)))
    span = max(36, dx * factor * 1.3, (hi - lo) * 1.6)
    scale = 400 / span

    def project(p):
        delta = p[0] - lon
        if iso3 != "USA":
            delta = (delta + 180) % 360 - 180
        return (200 + delta * factor * scale, 150 - (p[1] - lat) * scale)

    for latline in range(-60, 91, 10):
        y = project((lon, latline))[1]
        el(group, "line", x1=0, x2=400, y1=y, y2=y, class_="map-grid")
    for lonline in range(-180, 181, 10):
        x = project((lonline, lat))[0]
        el(group, "line", x1=x, x2=x, y1=0, y2=320, class_="map-grid")
    for _code, geom in world.items():
        el(group, "path", d=path(geom, project), class_="country", fill_rule="evenodd")
    el(group, "path", d=path(country, project), class_="country selected", fill_rule="evenodd")
    x, y = project((lon, lat))
    el(group, "circle", cx=x, cy=y, r=11, class_="locator-dot")
    text(group, x + 18, y + 8, name, class_="map-country-name")
    if iso3 == "TWN":
        for label, x, y in [("CHINE", 40, 92), ("JAPON", 284, 45), ("PHILIPPINES", 174, 260)]:
            text(group, x, y, label, class_="map-region-label")
        text(group, 292, 195, "Pacifique", class_="map-sea-label")
    # The world inset is geographical context, not a second full figure.
    inset = el(root, "svg", x=14, y=225, width=122, height=78, viewBox="0 0 360 180")
    el(inset, "rect", width=360, height=180, fill="var(--bg)", rx=8)

    def worldproject(p):
        return (p[0] + 180, 90 - p[1])

    for geom in world.values():
        el(inset, "path", d=path(geom, worldproject), fill="var(--land)")
    el(
        inset,
        "circle",
        cx=lon + 180,
        cy=90 - lat,
        r=10,
        fill="none",
        stroke="var(--accent)",
        stroke_width=4,
    )
    caption = {
        "TWN": "Dans le Pacifique occidental",
        "USA": "États contigus · repère mondial",
    }.get(iso3, "Situation régionale")
    return (
        f'<figure class="locator" id="situation">{finish(root)}'
        f"<figcaption>{caption}{marker}</figcaption></figure>"
    )


def cities(
    iso3,
    name,
    city_data,
    geo_dir,
    marker="",
    title="Villes principales",
    scope="Population municipale",
):
    geom = load_geo(geo_dir, "countries-50m.json")[iso3]
    if iso3 == "USA":
        geom = contiguous_usa(geom)
    start, dx, lo, hi = main_bounds(geom)
    factor = max(0.15, cos(radians((lo + hi) / 2)))
    scale = min(205 / max(dx * factor, 0.02), 290 / max(hi - lo, 0.02))

    def project(p):
        return (
            130 + (((p[0] % 360 - start) % 360) * factor - dx * factor / 2) * scale,
            166 - (p[1] - (lo + hi) / 2) * scale,
        )

    root = canvas(f"Villes de {name}, repères numérotés du tableau", 260, 360)
    defs = el(root, "defs")
    clip = el(defs, "clipPath", id=f"cities-frame-{iso3}")
    el(clip, "rect", width=260, height=360)
    group = el(root, "g", clip_path=f"url(#cities-frame-{iso3})")
    el(group, "rect", width=260, height=360, fill="var(--map-sea)", rx=6)
    el(group, "path", d=path(geom, project), class_="city-land", fill_rule="evenodd")
    north = [i for i, c in enumerate(city_data) if iso3 == "TWN" and c["lat"] > 24.8]

    def pin(parent, x, y, i):
        el(parent, "circle", cx=x, cy=y, r=11, class_="city-dot")
        text(parent, x, y + 6, i + 1, text_anchor="middle", class_="pin-number")

    for i, city in enumerate(city_data):
        if i not in north:
            x, y = project((city["lon"], city["lat"]))
            offsets = (
                {
                    "New York": (8, -15),
                    "Philadelphie": (8, 15),
                    "Los Angeles": (-8, -10),
                    "Phoenix": (8, 10),
                }
                if iso3 == "USA"
                else {}
            )
            ox, oy = offsets.get(city["name"], (0, 0))
            if ox or oy:
                el(
                    group,
                    "line",
                    x1=x,
                    y1=y,
                    x2=x + ox,
                    y2=y + oy,
                    stroke="var(--accent)",
                    stroke_width=1,
                )
                el(group, "circle", cx=x, cy=y, r=2, fill="var(--accent)")
            pin(group, x + ox, y + oy, i)
    if north:
        x, y = project((121.5, 25))
        el(
            group,
            "circle",
            cx=x,
            cy=y,
            r=16,
            fill="none",
            stroke="var(--accent)",
            stroke_dasharray="3 3",
        )
        el(
            group,
            "line",
            x1=x - 15,
            x2=118,
            y1=y,
            y2=72,
            stroke="var(--accent)",
            stroke_dasharray="3 3",
        )
        inset = el(group, "svg", x=8, y=8, width=120, height=92, viewBox="0 0 120 103")
        el(
            inset,
            "rect",
            x=1,
            y=1,
            width=118,
            height=101,
            rx=4,
            fill="var(--bg)",
            stroke="var(--rule)",
        )

        def ip(p):
            return (15 + (p[0] - 121.24) * 250, 81 - (p[1] - 24.92) * 250)

        el(inset, "path", d=path(geom, ip), class_="city-land")
        el(inset, "rect", x=6, y=6, width=76, height=23, fill="var(--bg)", rx=2)
        text(inset, 10, 23, "Le nord", class_="inset-label")
        for i in north:
            pin(inset, *ip((city_data[i]["lon"], city_data[i]["lat"])), i)
    text(group, 230, 291, "N", text_anchor="middle")
    el(
        group,
        "path",
        d="M230 300 V326 M225 306 L230 300 L235 306",
        fill="none",
        stroke="var(--ink)",
        stroke_width=1.5,
    )
    km = 1000 if iso3 == "USA" else (100 if (hi - lo) > 1 else 1)
    distance = km / 111.2 * scale
    el(
        group,
        "path",
        d=f"M18 326 v5 h{distance:.2f} v-5",
        fill="none",
        stroke="var(--ink)",
        stroke_width=2,
    )
    text(group, 18, 350, f"{km} km")
    rows = []
    for i, c in enumerate(city_data):
        rows.append(
            f'<tr><th scope="row"><span class="city-number">{i + 1:02d}</span> '
            f"{escape(c['name'])}</th>"
            f'<td class="city-pop">{quantity(c["population"], "habitants")}</td>'
            f'<td class="city-role">{escape(c.get("note", ""))}</td></tr>'
        )
    table = (
        f'<table class="cities-table"><caption>{escape(scope)}</caption>'
        "<thead><tr><th>Ville</th><th>Population</th><th>Repère</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    note = (
        "Carte des États contigus. Populations municipales, hors agglomérations."
        if iso3 == "USA"
        else "Les limites municipales englobent aussi des espaces ruraux."
    )
    return (
        f'<figure class="graphic cities-figure" id="villes"><h3>{escape(title)}{marker}</h3>'
        f'<p class="figure-note">{note}</p>'
        f'<div class="cities-layout">{finish(root)}{table}</div></figure>'
    )
