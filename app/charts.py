"""Small dependency-free SVG renderers for the fiche data contract."""

from html import escape
from math import ceil, isfinite
from xml.etree.ElementTree import Element, SubElement, tostring

W, H = 680, 380
LEFT, RIGHT, TOP, BOTTOM = 82, 600, 42, 300
COLORS = [
    "var(--series-1)",
    "var(--series-2)",
    "var(--series-3)",
    "var(--series-4)",
    "var(--series-5)",
    "var(--series-6)",
]
MONTHS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]


def el(parent, tag, **attrs):
    return SubElement(
        parent, tag, {k.removesuffix("_").replace("_", "-"): str(v) for k, v in attrs.items()}
    )


def text(parent, x, y, value, **attrs):
    node = el(parent, "text", x=x, y=y, **attrs)
    node.text = str(value)
    return node


def svg(chart, height=H):
    root = Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {W} {height}",
            "role": "img",
            "class": "chart",
        },
    )
    SubElement(root, "title").text = str(chart["title"])
    SubElement(root, "desc").text = "Données détaillées dans le tableau sous le graphique."
    return root


def numbers(values):
    result = [float(v) for v in values]
    if not result or not all(isfinite(v) for v in result):
        raise ValueError("Chart values must be finite and non-empty")
    return result


def pairs(labels, values):
    vals = numbers(values)
    if len(labels) != len(vals):
        raise ValueError("Chart labels and values must have equal lengths")
    return vals


def fmt(value):
    return f"{value:,.1f}".rstrip("0").rstrip(".").replace(",", "\u202f").replace(".", ",")


def extent(values):
    low, high = min(0, min(values)), max(0, max(values))
    if low == high:
        high = low + 1
    return low, high


def yscale(low, high):
    return lambda value: BOTTOM - (value - low) / (high - low) * (BOTTOM - TOP)


def axes(root, low, high, unit):
    y = yscale(low, high)
    text(root, LEFT, 23, unit, class_="axis-unit")
    for i in range(5):
        value = low + (high - low) * i / 4
        pos = y(value)
        el(root, "line", x1=LEFT, x2=RIGHT, y1=pos, y2=pos, class_="grid")
        text(root, LEFT - 10, pos + 5, fmt(value), text_anchor="end")
    return y


def label(root, x, y, value, anchor="middle", max_chars=15):
    words = str(value).split()
    lines = [""]
    for word in words:
        if len(lines[-1]) + len(word) > max_chars and lines[-1]:
            lines.append("")
        lines[-1] = (lines[-1] + " " + word).strip()
    node = text(root, x, y, "", text_anchor=anchor)
    for i, line in enumerate(lines):
        el(node, "tspan", x=x, dy=0 if i == 0 else 19).text = line


def finish(root):
    return tostring(root, encoding="unicode")


def climate(chart):
    root = svg(chart)
    tmin, tmax, rain = (pairs(MONTHS, chart[k]) for k in ("tmin", "tmax", "precip_mm"))
    low, high = extent(tmin + tmax)
    low, high = min(0, low), max(10, high)
    y = axes(root, low, high, "°C")
    rainmax = max(10, ceil(max(rain) / 50) * 50)
    text(root, RIGHT + 30, 23, "mm", text_anchor="middle")
    for i in range(5):
        text(root, RIGHT + 12, BOTTOM - i * (BOTTOM - TOP) / 4 + 5, fmt(rainmax * i / 4))
    step = (RIGHT - LEFT) / 12
    for i, value in enumerate(rain):
        height = value / rainmax * (BOTTOM - TOP)
        el(
            root,
            "rect",
            x=LEFT + i * step + step * 0.2,
            y=BOTTOM - height,
            width=step * 0.6,
            height=height,
            fill=COLORS[1],
            opacity="0.65",
        )
        text(root, LEFT + (i + 0.5) * step, BOTTOM + 27, MONTHS[i])
    for values, color, dash in ((tmin, COLORS[0], "6 4"), (tmax, COLORS[2], "none")):
        el(
            root,
            "polyline",
            points=" ".join(f"{LEFT + (i + 0.5) * step},{y(v)}" for i, v in enumerate(values)),
            fill="none",
            stroke=color,
            stroke_width=3,
            stroke_dasharray=dash,
        )
    for i, (name, color) in enumerate(
        (("Min. °C (tirets)", COLORS[0]), ("Max. °C", COLORS[2]), ("Pluie mm", COLORS[1]))
    ):
        text(root, LEFT + i * 185, 367, name, fill=color)
    return finish(root)


def bar(chart):
    vals = pairs(chart["labels"], chart["values"])
    root = svg(chart, 440)
    y = axes(root, *extent(vals), chart["unit"])
    step = (RIGHT - LEFT) / len(vals)
    for i, (name, value) in enumerate(zip(chart["labels"], vals, strict=True)):
        x = LEFT + step * (i + 0.15)
        el(
            root,
            "rect",
            x=x,
            y=min(y(0), y(value)),
            width=step * 0.7,
            height=abs(y(0) - y(value)),
            fill=COLORS[2] if name == chart.get("highlight") else COLORS[0],
        )
        label(root, x + step * 0.35, BOTTOM + 25, name, max_chars=max(5, int(step / 9)))
    return finish(root)


def barh(chart):
    vals = pairs(chart["labels"], chart["values"])
    height = 95 + len(vals) * 64
    root = svg(chart, height)
    low, high = extent(vals)

    def x(v):
        return 260 + (v - low) / (high - low) * 310

    text(root, 570, 24, chart["unit"], text_anchor="end")
    for i in range(5):
        pos = 260 + i * 310 / 4
        el(root, "line", x1=pos, x2=pos, y1=40, y2=height - 45, class_="grid")
        text(root, pos, height - 16, fmt(low + i * (high - low) / 4))
    for i, (name, value) in enumerate(zip(chart["labels"], vals, strict=True)):
        y = 52 + i * 64
        label(root, 245, y + 15, name, "end", 23)
        el(
            root,
            "rect",
            x=min(x(0), x(value)),
            y=y,
            width=abs(x(value) - x(0)),
            height=26,
            fill=COLORS[2] if name == chart.get("highlight") else COLORS[0],
        )
        text(root, 590, y + 20, fmt(value))
    return finish(root)


def pyramid(chart):
    labels = chart["age_groups"]
    male, female = pairs(labels, chart["male"]), pairs(labels, chart["female"])
    root = svg(chart, 130 + len(labels) * 30)
    limit = max(male + female) or 1
    base = 65 + len(labels) * 30
    text(root, 160, 25, "Hommes")
    text(root, 445, 25, "Femmes")
    for i, name in enumerate(labels):
        y = base - (i + 1) * 30
        text(root, 340, y + 18, name, text_anchor="middle")
        for val, start, color in (
            (male[i], 290 - male[i] / limit * 205, COLORS[0]),
            (female[i], 390, COLORS[1]),
        ):
            el(root, "rect", x=start, y=y, width=val / limit * 205, height=22, fill=color)
    for fraction in (0, 0.5, 1):
        for pos in (290 - fraction * 205, 390 + fraction * 205):
            text(root, pos, base + 20, fmt(fraction * limit), text_anchor="middle")
    text(root, 340, base + 52, chart["unit"], text_anchor="middle")
    return finish(root)


def stacked(chart):
    labels = chart["labels"]
    series = chart["series"]
    vals = [pairs(labels, s["values"]) for s in series]
    if any(v < 0 for row in vals for v in row):
        raise ValueError("Stacked charts require non-negative values")
    totals = [sum(row[i] for row in vals) for i in range(len(labels))]
    root = svg(chart, 450 + len(series) * 26)
    y = axes(root, 0, max(totals) or 1, chart["unit"])
    step = (RIGHT - LEFT) / len(labels)
    for i, name in enumerate(labels):
        base = 0
        for j, row in enumerate(vals):
            el(
                root,
                "rect",
                x=LEFT + step * (i + 0.2),
                y=y(base + row[i]),
                width=step * 0.6,
                height=y(base) - y(base + row[i]),
                fill=COLORS[j % len(COLORS)],
            )
            base += row[i]
        label(root, LEFT + step * (i + 0.5), BOTTOM + 26, name)
    for j, s in enumerate(series):
        text(root, LEFT, 430 + j * 26, s["name"], fill=COLORS[j % len(COLORS)])
    return finish(root)


def line(chart):
    labels, series = chart["x"], chart["series"]
    vals = [pairs(labels, s["values"]) for s in series]
    root = svg(chart, 440 + len(series) * 26)
    y = axes(root, *extent([v for row in vals for v in row]), chart["unit"])

    def x(i):
        return LEFT + i / max(1, len(labels) - 1) * (RIGHT - LEFT)

    for j, row in enumerate(vals):
        color = COLORS[j % len(COLORS)]
        el(
            root,
            "polyline",
            points=" ".join(f"{x(i)},{y(v)}" for i, v in enumerate(row)),
            fill="none",
            stroke=color,
            stroke_width=3,
            stroke_dasharray="none" if j == 0 else f"{j * 3} 4",
        )
        for i, v in enumerate(row):
            el(root, "circle", cx=x(i), cy=y(v), r=4, fill=color)
        text(root, LEFT, 420 + j * 26, series[j]["name"], fill=color)
    for i, name in enumerate(labels):
        if i % max(1, ceil(len(labels) / 8)) == 0 or i == len(labels) - 1:
            label(root, x(i), BOTTOM + 25, name, max_chars=8)
    return finish(root)


def share(chart):
    vals = pairs(chart["labels"], chart["values"])
    total = sum(vals)
    if total <= 0 or any(v < 0 for v in vals):
        raise ValueError("Share charts require positive totals")
    root = svg(chart, 140 + len(vals) * 32)
    x = LEFT
    for i, (name, val) in enumerate(zip(chart["labels"], vals, strict=True)):
        width = (RIGHT - LEFT) * val / total
        el(root, "rect", x=x, y=40, width=width, height=45, fill=COLORS[i % len(COLORS)])
        x += width
        el(root, "rect", x=LEFT, y=125 + i * 32, width=16, height=16, fill=COLORS[i % len(COLORS)])
        text(root, LEFT + 28, 139 + i * 32, f"{name} : {fmt(val)} {chart['unit']}")
    text(root, LEFT, 109, "0 %")
    text(root, RIGHT, 109, "100 %", text_anchor="end")
    return finish(root)


RENDERERS = {fn.__name__: fn for fn in (climate, pyramid, bar, barh, stacked, line, share)}


def data_table(chart):
    kind = chart["type"]
    if kind == "climate":
        headers = ["Mois", "Min. (°C)", "Max. (°C)", "Pluie (mm)"]
        rows = zip(MONTHS, chart["tmin"], chart["tmax"], chart["precip_mm"], strict=True)
    elif kind == "pyramid":
        headers = ["Âge", f"Hommes ({chart['unit']})", f"Femmes ({chart['unit']})"]
        rows = zip(chart["age_groups"], chart["male"], chart["female"], strict=True)
    elif kind in ("stacked", "line"):
        headers = ["Période"] + [f"{s['name']} ({chart['unit']})" for s in chart["series"]]
        rows = zip(
            chart["x" if kind == "line" else "labels"],
            *(s["values"] for s in chart["series"]),
            strict=True,
        )
    else:
        headers = ["Catégorie", chart["unit"]]
        rows = zip(chart["labels"], chart["values"], strict=True)
    head = "".join(f"<th scope='col'>{escape(str(h))}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>" for row in rows
    )
    return (
        "<details><summary>Voir les données</summary><div class='table-wrap'>"
        f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></details>"
    )


def render_chart(chart):
    drawing = RENDERERS[chart["type"]](chart)
    title = escape(str(chart["title"]))
    source = escape(str(chart["source"]))
    year = escape(str(chart["year"]))
    note = f"<p>{escape(str(chart['note']))}</p>" if chart.get("note") else ""
    place = f" · {escape(str(chart['place']))}" if chart.get("place") else ""
    return (
        f"<figure class='graphic'><h3>{title}{place}</h3>{drawing}"
        f"<figcaption>Source : {source} · {year}</figcaption>"
        f"{note}{data_table(chart)}</figure>"
    )
