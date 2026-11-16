"""Regional locators and numbered overlays on licensed country maps."""

import json
from functools import lru_cache
from html import escape
from math import cos, isfinite, radians, sin
from pathlib import Path
from urllib.parse import quote
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


def path(geometry, project, longitude_center=None):
    outlines = []
    for ring in rings(geometry):
        if longitude_center is None:
            copies = [ring]
        else:
            # Keep each ring continuous at the regional projection's opposite meridian.
            # Wrapping vertices separately draws distant coasts across the whole map.
            previous, unwrapped = longitude_center, []
            for lon, lat in ring:
                lon = previous + (lon - previous + 180) % 360 - 180
                unwrapped.append((lon, lat))
                previous = lon
            copies = [[(lon + shift, lat) for lon, lat in unwrapped] for shift in (-360, 0, 360)]
        for copy in copies:
            outlines.append(
                "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in map(project, copy)) + " Z"
            )
    return " ".join(outlines)


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


def focus(geometry, bbox):
    """Keep the polygons inside bbox [lon_min, lat_min, lon_max, lat_max] (e.g. a mainland)."""
    if not bbox:
        return geometry
    w, s, e, n = bbox
    polygons = (
        geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    )
    kept = [
        poly for poly in polygons if all(w <= lon <= e and s <= lat <= n for lon, lat in poly[0])
    ]
    return {"type": "MultiPolygon", "coordinates": kept} if kept else geometry


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


def locator(iso3, name, geo_dir, marker="", map_focus=None):
    map_focus = map_focus or {}
    world = load_geo(geo_dir, "world-110m.json")
    country = focus(load_geo(geo_dir, "countries-50m.json")[iso3], map_focus.get("bbox"))
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
        return (200 + ((p[0] - lon + 180) % 360 - 180) * factor * scale, 150 - (p[1] - lat) * scale)

    def continuous_project(p):
        return (200 + (p[0] - lon) * factor * scale, 150 - (p[1] - lat) * scale)

    for latline in range(-60, 91, 10):
        y = project((lon, latline))[1]
        el(group, "line", x1=0, x2=400, y1=y, y2=y, class_="map-grid")
    for lonline in range(-180, 181, 10):
        x = project((lonline, lat))[0]
        el(group, "line", x1=x, x2=x, y1=0, y2=320, class_="map-grid")
    for _code, geom in world.items():
        el(
            group,
            "path",
            d=path(geom, continuous_project, lon),
            class_="country",
            fill_rule="evenodd",
        )
    el(
        group,
        "path",
        d=path(country, continuous_project, lon),
        class_="country selected",
        fill_rule="evenodd",
    )
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
    caption = escape(
        map_focus.get("caption")
        or ("Dans le Pacifique occidental" if iso3 == "TWN" else "Situation régionale")
    )
    return (
        f'<figure class="locator" id="situation">{finish(root)}'
        f"<figcaption>{caption}{marker}</figcaption></figure>"
    )


def map_point(map_data, point):
    """Project lon/lat to fractions of the original image, using Wikipedia's module."""
    lon, lat = point
    projection = map_data["projection"]
    kind = projection["type"]
    if kind == "equirectangular":
        bounds = map_data["bounds"]
        width = (bounds["right"] - bounds["left"]) % 360 or 360
        return (
            (lon - bounds["left"]) % 360 / width,
            (bounds["top"] - lat) / (bounds["top"] - bounds["bottom"]),
        )
    if kind == "equidistant_conic":
        radius = projection["radius_offset"] - radians(lat)
        angle = projection["cone"] * radians(lon - projection["longitude0"])
        x = 50 + projection["scale"] * radius * sin(angle)
        y = 50 + projection["scale"] * projection["y_scale"] * (
            projection["y_offset"] - projection["radius0"] + radius * cos(angle)
        )
        return x / 100, y / 100
    raise ValueError(f"Unsupported city map projection: {kind}")


def validate_city_map(map_data, assets):
    """Reject missing assets or incomplete georeferencing before serving a fiche."""
    if not map_data:
        raise ValueError("cities_map is required for the city figure")
    filename = map_data["file"]
    if Path(filename).name != filename or Path(filename).suffix not in {".svg", ".webp"}:
        raise ValueError("cities_map.file must be a local SVG or WebP asset name")
    asset = assets / filename
    if not asset.is_file() or not asset.resolve().is_relative_to(assets.resolve()):
        raise ValueError(f"Missing city map asset: {filename}")
    if asset.stat().st_size > 400_000:
        raise ValueError("City map assets must be at most 400 KB")
    for key in ("width", "height"):
        if not isfinite(map_data[key]) or map_data[key] <= 0:
            raise ValueError(f"cities_map.{key} must be positive")
    credit = map_data["credit"]
    if not all(credit.get(key) for key in ("author", "license", "url", "license_url")):
        raise ValueError("City map credit needs author, license, url and license_url")
    if not map_data.get("source_ids"):
        raise ValueError("City map credit needs source_ids")
    projection = map_data["projection"]
    if projection["type"] == "equirectangular":
        bounds = map_data["bounds"]
        if not all(isfinite(bounds[key]) for key in ("top", "bottom", "left", "right")):
            raise ValueError("City map bounds must be finite")
        if not -90 <= bounds["bottom"] < bounds["top"] <= 90:
            raise ValueError("City map needs bottom < top within latitude limits")
        if bounds["left"] == bounds["right"]:
            raise ValueError("City map needs distinct longitude bounds")
    elif projection["type"] == "equidistant_conic":
        keys = ("radius_offset", "cone", "longitude0", "scale", "y_scale", "y_offset", "radius0")
        if not all(isfinite(projection[key]) for key in keys):
            raise ValueError("City map projection parameters must be finite")
    else:
        raise ValueError(f"Unsupported city map projection: {projection['type']}")


def cities(
    iso3,
    name,
    city_data,
    map_data,
    marker="",
    title="Villes principales",
    scope="Population municipale",
    note="Les limites municipales englobent aussi des espaces ruraux.",
    inset=None,
):
    # Fit the full image without cropping or changing its aspect ratio.
    image_w = 244
    image_h = image_w * map_data["height"] / map_data["width"]
    height = max(image_h + 16, (inset["y"] + inset["height"] + 8) if inset else 0)
    root = canvas(f"Villes de {name}, repères numérotés du tableau", 260, round(height, 3))
    href = f"/pays/{iso3}/assets/{quote(map_data['file'])}"

    def background(parent, x, y, zoom=1):
        el(
            parent,
            "image",
            href=href,
            x=x,
            y=y,
            width=image_w * zoom,
            height=image_h * zoom,
            preserveAspectRatio="none",
            class_="city-map-image",
        )

    def project(p):
        x, y = map_point(map_data, p)
        return 8 + x * image_w, 8 + y * image_h

    background(root, 8, 8)
    grouped = [i for i, c in enumerate(city_data) if inset and c["name"] in inset["cities"]]

    def pin(parent, x, y, i, city, origin):
        ox, oy = city.get("offset", (0, 0))
        if ox or oy:
            el(parent, "line", x1=x, y1=y, x2=x + ox, y2=y + oy, class_="city-leader")
            el(parent, "circle", cx=x, cy=y, r=2.5, class_="city-anchor")
        dot = el(
            parent,
            "g",
            class_="city-pin",
            data_city=city["name"],
            data_origin_x=origin[0],
            data_origin_y=origin[1],
        )
        el(dot, "title").text = f"{i + 1}. {city['name']}"
        el(dot, "circle", cx=x + ox, cy=y + oy, r=11, class_="city-dot")
        text(dot, x + ox, y + oy + 6, i + 1, text_anchor="middle", class_="pin-number")

    for i, city in enumerate(city_data):
        point = (city["lon"], city["lat"])
        u, v = map_point(map_data, point)
        if not (0 <= u <= 1 and 0 <= v <= 1):
            raise ValueError(f"City outside licensed map: {city['name']}")
        if i not in grouped:
            pin(root, *project(point), i, city, project(point))
    if grouped:
        # The inset reuses the same image and projection, with a single zoom/pan transform.
        bx, by, bw, bh = (inset[key] for key in ("x", "y", "width", "height"))
        zoom = inset["zoom"]
        cx, cy = project(inset["center"])
        left, top = bw / 2 - (cx - 8) * zoom, (bh + 26) / 2 - (cy - 8) * zoom
        frame = el(
            root,
            "svg",
            x=bx,
            y=by,
            width=bw,
            height=bh,
            viewBox=f"0 0 {bw} {bh}",
            class_="city-inset",
            overflow="hidden",
        )
        background(frame, left, top, zoom)
        el(frame, "rect", x=0, y=0, width=bw, height=26, fill="var(--bg)")
        text(frame, 8, 20, inset["label"], class_="inset-label")
        for i in grouped:
            city = city_data[i]
            x, y = project((city["lon"], city["lat"]))
            px, py = left + (x - 8) * zoom, top + (y - 8) * zoom
            ox, oy = city.get("offset", (0, 0))
            if not (11 <= px + ox <= bw - 11 and 37 <= py + oy <= bh - 11):
                raise ValueError(f"City pin clipped in inset: {city['name']}")
            pin(frame, px, py, i, city, (x, y))
        el(
            frame,
            "rect",
            x=1,
            y=1,
            width=bw - 2,
            height=bh - 2,
            fill="none",
            stroke="var(--rule)",
            stroke_width=2,
        )
        # A box marks the exact enlarged area; it does not hide the main map.
        el(
            root,
            "rect",
            x=8 - left / zoom,
            y=8 + (26 - top) / zoom,
            width=bw / zoom,
            height=(bh - 26) / zoom,
            fill="none",
            class_="city-inset-area",
        )
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
    return (
        f'<figure class="graphic cities-figure" id="villes"><h3>{escape(title)}{marker}</h3>'
        f'<p class="figure-note">{escape(note)}</p>'
        f'<div class="cities-layout">{finish(root)}{table}</div></figure>'
    )
