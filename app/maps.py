"""SVG maps using the committed Natural Earth geometry only."""

import json
from functools import lru_cache
from html import escape
from math import cos, radians, sqrt
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

from .charts import el, finish, text


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


def canvas(title, height):
    root = Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 680 {height}",
            "role": "img",
            "class": "map",
        },
    )
    SubElement(root, "title").text = title
    return root


def figure(title, drawing, scale, extra=""):
    return (
        f"<figure class='graphic'><h3>{escape(title)}</h3>{drawing}<figcaption>Source : "
        "<a href='https://www.naturalearthdata.com/'>Natural Earth</a> · "
        f"{scale} · domaine public</figcaption>{extra}</figure>"
    )


def locator(iso3, name, geo_dir):
    world = load_geo(geo_dir, "world-110m.json")
    country = load_geo(geo_dir, "countries-50m.json")[iso3]
    root = canvas(f"Situation de {name} dans le monde", 360)

    def project(p):
        return ((p[0] + 180) / 360 * 680, (90 - p[1]) / 180 * 340 + 10)

    for code, geom in world.items():
        el(
            root,
            "path",
            d=path(geom, project),
            class_="country selected" if code == iso3 else "country",
            fill_rule="evenodd",
        )
    # At world scale, microstates need a marker in addition to their actual outline.
    points = [p for ring in rings(country) for p in ring]
    minx, maxx = min(p[0] for p in points), max(p[0] for p in points)
    miny, maxy = min(p[1] for p in points), max(p[1] for p in points)
    if iso3 not in world or (maxx - minx) * (maxy - miny) < 3:
        el(root, "path", d=path(country, project), class_="country selected")
        x, y = project(((minx + maxx) / 2, (miny + maxy) / 2))
        el(root, "circle", cx=x, cy=y, r=5, class_="locator-dot")
    return figure(f"{name} dans le monde", finish(root), "1:110 m")


def cities(iso3, name, city_data, geo_dir):
    geom = load_geo(geo_dir, "countries-50m.json")[iso3]
    polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]

    def area(polygon):
        ring = polygon[0]
        return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:], strict=False)))

    largest = max(area(polygon) for polygon in polygons)
    # Keep sizeable islands in the frame, without shrinking France to include Guiana.
    # All geometry is still drawn, clipped to the main territory and listed cities.
    coordinates = [
        point for polygon in polygons if area(polygon) >= largest * 0.25 for point in polygon[0]
    ]
    coordinates += [[c["lon"], c["lat"]] for c in city_data]
    # Choose the shortest longitude interval, keeping Pacific countries continuous.
    longitudes = sorted(p[0] % 360 for p in coordinates)
    gaps = [
        (
            longitudes[(i + 1) % len(longitudes)]
            + (360 if i == len(longitudes) - 1 else 0)
            - value,
            i,
        )
        for i, value in enumerate(longitudes)
    ]
    _, index = max(gaps)
    start = longitudes[(index + 1) % len(longitudes)]

    def wrap(lon):
        return (lon % 360 - start) % 360

    xvalues = [wrap(p[0]) for p in coordinates]
    minlat, maxlat = min(p[1] for p in coordinates), max(p[1] for p in coordinates)
    factor = max(0.15, cos(radians((minlat + maxlat) / 2)))
    dx, dy = max(max(xvalues), 0.02) * factor, max(maxlat - minlat, 0.02)
    scale = min(480 / dx, 360 / dy)

    def project(p):
        return (
            340 + (wrap(p[0]) * factor - dx / 2) * scale,
            225 - (p[1] - (minlat + maxlat) / 2) * scale,
        )

    root = canvas(
        f"Villes principales de {name}. Taille des points proportionnelle à la population.", 470
    )
    defs = el(root, "defs")
    clip = el(defs, "clipPath", id=f"cities-frame-{iso3}")
    el(clip, "rect", x=8, y=8, width=664, height=425)
    el(
        root,
        "path",
        d=path(geom, project),
        class_="country selected",
        fill_rule="evenodd",
        clip_path=f"url(#cities-frame-{iso3})",
    )
    maxpop = max((c["population"] for c in city_data), default=1) or 1
    occupied = []
    for city in sorted(city_data, key=lambda c: -c["population"]):
        x, y = project((city["lon"], city["lat"]))
        radius = max(3, sqrt(max(0, city["population"]) / maxpop) * 14)
        dot = el(root, "circle", cx=x, cy=y, r=radius, class_="city-dot")
        SubElement(dot, "title").text = f"{city['name']} : {city['population']:,} habitants"
        width = min(280, len(city["name"]) * 9)
        tx = max(12, min(x + radius + 7, 668 - width))
        ty = max(22, min(y + 5, 440))
        for _ in range(len(city_data) * 2 + 1):
            if all(
                tx + width < ox or ox + ow < tx or abs(ty - oy) >= 22 for ox, oy, ow in occupied
            ):
                break
            ty = ty + 24 if ty < 420 else 22
        occupied.append((tx, ty, width))
        el(root, "line", x1=x, y1=y, x2=tx, y2=ty - 5, class_="leader")
        text(root, tx, ty, city["name"], class_="city-label")
    text(root, 18, 455, "Points : population relative · Nord en haut")
    items = "".join(
        (
            f"<li><strong>{escape(c['name'])}</strong> : "
            f"{c['population']:,} habitants"
            f"{(' · ' + escape(c['note'])) if c.get('note') else ''}</li>"
        ).replace(",", "\u202f")
        for c in city_data
    )
    return figure(
        "Villes principales",
        finish(root),
        "admin-0 1:50 m (micro-États 1:10 m)",
        "<p>Cadrage sur le territoire principal et les villes indiquées.</p>"
        f"<ul class='city-list'>{items}</ul>",
    )
