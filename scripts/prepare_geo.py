"""Rebuild the compact, committed Natural Earth extract. No runtime download.

Run: uv run --with pyshp --with shapely python scripts/prepare_geo.py
"""

import csv
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import shapefile
from shapely.geometry import mapping, shape

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data/geo"
ALIASES = {"KOS": "XKX", "SDS": "SSD", "PSX": "PSE"}


def download(scale):
    url = (
        f"https://naturalearth.s3.amazonaws.com/{scale}m_cultural/ne_{scale}m_admin_0_countries.zip"
    )
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    stem = f"ne_{scale}m_admin_0_countries"
    reader = shapefile.Reader(
        **{ext: io.BytesIO(archive.read(f"{stem}.{ext}")) for ext in ("shp", "shx", "dbf")},
        encoding="utf-8",
    )
    result = {}
    for feature in reader.iterShapeRecords():
        props = feature.record.as_dict()
        code = ALIASES.get(props["ADM0_A3"], props["ADM0_A3"])
        result[code] = feature.shape.__geo_interface__
    return result


def rounded(value):
    if isinstance(value, (list, tuple)):
        return [rounded(item) for item in value]
    return round(value, 3) if isinstance(value, float) else value


def save(name, features, tolerance):
    simplified = {}
    for code, geo in features.items():
        geom = shape(geo).simplify(tolerance, preserve_topology=True)
        simplified[code] = {
            "type": geom.geom_type,
            "coordinates": rounded(mapping(geom)["coordinates"]),
        }
    path = TARGET / name
    path.write_text(json.dumps(simplified, separators=(",", ":")) + "\n")
    print(f"{path.relative_to(ROOT)}: {path.stat().st_size:,} bytes, {len(features)} features")


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    codes = {row["iso3"] for row in csv.DictReader((ROOT / "data/ordre.csv").open())}
    world = download(110)
    countries = {code: geo for code, geo in download(50).items() if code in codes}
    missing = codes - countries.keys()
    if missing:
        countries.update({code: geo for code, geo in download(10).items() if code in missing})
    if codes - countries.keys():
        raise ValueError(f"Missing countries: {codes - countries.keys()}")
    save("world-110m.json", world, 0.02)
    save("countries-50m.json", countries, 0.005)


if __name__ == "__main__":
    main()
