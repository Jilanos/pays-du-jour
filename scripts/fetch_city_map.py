"""Fetch a licensed Commons location map and print its candidate fiche records.

uv run --with cairosvg --with pillow python scripts/fetch_city_map.py MAR Morocco
Review stdout, then add cities_map and source to data.json. No data.json is overwritten.
For custom x/y modules, supply a reviewed projection with --projection-from data.json.
"""

import argparse
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    request = Request(url, headers={"User-Agent": "PaysDuJour/1.0 (country map research)"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def plain(value):
    return " ".join(unescape(re.sub(r"<[^>]+>", "", value)).split())


def download(iso3, country, projection_from=None):
    if not re.fullmatch(r"[A-Z]{3}", iso3):
        raise ValueError("ISO3 must contain three uppercase letters")
    module_url = "https://en.wikipedia.org/wiki/Module:Location_map/data/" + country.replace(
        " ", "_"
    )
    page = fetch(module_url).decode()
    code = "\n".join(plain(p) for p in re.findall(r"<pre[^>]*>(.*?)</pre>", page, re.S))
    image = re.search(r"\bimage\s*=\s*'([^']+)'", code)[1]
    custom = re.search(r"\b[xy]\s*=", code)
    if custom:
        if projection_from is None:
            raise ValueError(
                f"Custom x/y formulas in {module_url}. Implement and test the matching projection, "
                "then use --projection-from with the reviewed fiche JSON."
            )
        reviewed = json.loads(projection_from.read_text())["cities_map"]
        if reviewed.get("definition_url") != module_url:
            raise ValueError("The reviewed projection must reference this exact module")
        projection = reviewed["projection"]
        if projection.get("type") not in {"equidistant_conic", "japan_side_map", "spain_side_map"}:
            raise ValueError("Custom x/y formulas require a supported projection")
        if projection.get("type") == "japan_side_map" and country != "Japan":
            raise ValueError("Japan side map requires the Japan module")
        if projection.get("type") == "spain_side_map" and country != "Spain":
            raise ValueError("Spain side map requires the Spain module")
        bounds = None
    else:
        projection = {"type": "equirectangular"}
        bounds = {
            key: float(re.search(r"\b" + key + r"\s*=\s*([-\d.]+)", code)[1])
            for key in ("top", "bottom", "left", "right")
        }
    query = urlencode(
        {
            "action": "query",
            "format": "json",
            "titles": "File:" + image,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
        }
    )
    pages = json.loads(fetch("https://commons.wikimedia.org/w/api.php?" + query))["query"]["pages"]
    info = next(iter(pages.values()))["imageinfo"][0]
    metadata = info["extmetadata"]
    license_name = plain(metadata["LicenseShortName"]["value"])
    if not (license_name.startswith("CC BY-SA") or license_name == "Public domain"):
        raise ValueError(f"Review this map's licence before reuse: {license_name}")
    credit = {
        "author": plain(metadata["Artist"]["value"]),
        "license": license_name,
        "license_url": metadata.get("LicenseUrl", {}).get(
            "value", "https://commons.wikimedia.org/wiki/Commons:Copyright_tags#Public_domain"
        ),
        "url": info["descriptionurl"],
    }
    original = fetch(info["url"])
    if len(original) <= 400_000 and image.lower().endswith(".svg"):
        content, extension, conversion = original, "svg", "SVG original conservé."
    else:
        from io import BytesIO

        import cairosvg
        from PIL import Image

        if image.lower().endswith(".svg"):
            original = cairosvg.svg2png(bytestring=original, output_width=1100)
        raster = Image.open(BytesIO(original))
        raster.thumbnail((1100, 1600))
        stream = BytesIO()
        raster.save(stream, format="WEBP", quality=90, method=6)
        content, extension = stream.getvalue(), "webp"
        conversion = "Réduction proportionnelle et conversion WebP, sans recadrage ni recoloration."
    if len(content) > 400_000:
        raise ValueError("Map still exceeds 400 KB. Choose a simpler source or review compression.")
    folder = ROOT / "fiches" / iso3 / "assets"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"cities.{extension}"
    (folder / filename).write_bytes(content)
    return {
        "cities_map": {
            "file": filename,
            "width": info["width"],
            "height": info["height"],
            "bounds": bounds,
            "projection": projection,
            "credit": credit,
            "definition_url": module_url,
            "source_ids": ["CITYMAP"],
        },
        "source": {
            "id": "CITYMAP",
            "text": f"[Wikimedia Commons, {image}]({credit['url']}). {credit['author']}, "
            f"[{credit['license']}]({credit['license_url']}). {conversion} "
            f"[Bornes et projection]({module_url}). Repères numérotés ajoutés à l’affichage.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iso3")
    parser.add_argument("country", help="Exact country name in the English Wikipedia module")
    parser.add_argument("--projection-from", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            download(args.iso3, args.country, args.projection_from), ensure_ascii=False, indent=2
        )
    )
