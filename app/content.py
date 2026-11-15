"""Read file-based fiches and resolve block placeholders before Markdown rendering."""

import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from html import escape
from urllib.parse import quote

import yaml
from markdown_it import MarkdownIt
from markupsafe import Markup

from .charts import render_chart
from .config import Settings
from .maps import cities, locator

PLACEHOLDER = re.compile(r"^\s*\{\{(keyfacts|chart:[\w-]+|map:(?:locator|cities|relief))\}\}\s*$")
ISO3 = re.compile(r"[A-Z]{3}\Z")


def placeholder_block(state, start_line, end_line, silent):
    """Recognize a placeholder line even without surrounding blank lines."""
    if state.sCount[start_line] - state.blkIndent >= 4:
        return False
    line = state.src[state.bMarks[start_line] + state.tShift[start_line] : state.eMarks[start_line]]
    match = PLACEHOLDER.fullmatch(line)
    if not match:
        return False
    if not silent:
        token = state.push("fiche_placeholder", "", 0)
        token.content = match[1]
        token.map = [start_line, start_line + 1]
        state.line = start_line + 1
    return True


@dataclass
class Fiche:
    meta: dict
    html: Markup
    toc: list[tuple[str, str]]
    flag: bool


def alphabetical(value):
    return "".join(
        c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c)
    )


def country_list(settings: Settings):
    with settings.order_path.open(encoding="utf-8-sig", newline="") as stream:
        countries = list(csv.DictReader(stream))
    for country in countries:
        country["available"] = (settings.content_dir / country["iso3"] / "fiche.md").is_file()
    return countries


def keyfacts(data):
    result = "<div class='keyfacts'><dl>"
    for item in data.get("keyfacts", []):
        result += (
            f"<div><dt>{escape(str(item['label']))}</dt>"
            f"<dd><strong>{escape(str(item['value']))}</strong>"
            f"<small>{escape(str(item['source']))} · "
            f"{escape(str(item['year']))}</small></dd></div>"
        )
    result += "</dl></div>"
    if data.get("indices"):
        result += (
            "<div class='table-wrap'><table><caption>Indices</caption><thead><tr>"
            "<th>Indice</th><th>Valeur</th><th>Rang</th><th>Année · source</th>"
            "</tr></thead><tbody>"
        )
        for item in data["indices"]:
            values = (
                item["name"],
                item["value"],
                item.get("rank", "—"),
                f"{item['year']} · {item['source']}",
            )
            result += "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in values) + "</tr>"
        result += "</tbody></table></div>"
    return result


def read_fiche(iso3: str, settings: Settings) -> Fiche:
    if not ISO3.fullmatch(iso3):
        raise FileNotFoundError(iso3)
    folder = settings.content_dir / iso3
    raw = (folder / "fiche.md").read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", raw, maxsplit=2, flags=re.MULTILINE)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"{iso3}: expected YAML front matter")
    meta = yaml.safe_load(parts[1])
    if meta["iso3"] != iso3:
        raise ValueError(f"{iso3}: front matter ISO3 mismatch")
    data = json.loads((folder / "data.json").read_text(encoding="utf-8"))
    charts = {chart["id"]: chart for chart in data.get("charts", [])}
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    md.block.ruler.before(
        "paragraph",
        "fiche_placeholder",
        placeholder_block,
        {"alt": ["paragraph", "reference", "blockquote", "list"]},
    )
    tokens = md.parse(parts[2])
    toc, counts = [], {}
    # Markdown block parsing leaves fenced and indented code examples untouched.
    for index, token in enumerate(tokens):
        if token.type == "inline" and tokens[index - 1].type == "heading_open":
            title = "".join(
                child.content
                for child in token.children or []
                if child.type in ("text", "code_inline")
            )
            slug = re.sub(r"[^a-z0-9]+", "-", alphabetical(title)).strip("-") or "section"
            counts[slug] = counts.get(slug, 0) + 1
            anchor = slug if counts[slug] == 1 else f"{slug}-{counts[slug]}"
            tokens[index - 1].attrSet("id", anchor)
            if tokens[index - 1].tag == "h2":
                toc.append((anchor, title))
        if token.type != "fiche_placeholder":
            continue
        key = token.content
        if key == "keyfacts":
            rendered = keyfacts(data)
        elif key.startswith("chart:"):
            rendered = render_chart(charts[key[6:]])
        elif key == "map:locator":
            rendered = locator(iso3, meta["nom"], settings.geo_dir)
        elif key == "map:cities":
            rendered = cities(iso3, meta["nom"], data.get("cities", []), settings.geo_dir)
        else:
            relief = next(
                (
                    p
                    for ext in ("jpg", "jpeg", "png", "webp", "svg")
                    if (p := folder / "assets" / f"relief.{ext}").is_file()
                ),
                None,
            )
            rendered = ""
            if meta.get("relief_pertinent") and relief:
                rendered = (
                    f"<figure><img src='/pays/{iso3}/assets/{quote(relief.name)}' "
                    f"alt='Relief de {escape(meta['nom'], quote=True)}'>"
                    "<figcaption>Relief · crédits dans les sources de la fiche.</figcaption>"
                    "</figure>"
                )
        token.type, token.content, token.children = "html_block", rendered, None
    return Fiche(
        meta,
        Markup(md.renderer.render(tokens, md.options, {})),
        toc,
        (folder / "assets/flag.svg").is_file(),
    )
