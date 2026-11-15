"""French numeric presentation. Source records always retain unrounded values."""

from datetime import date
from math import floor, isfinite, log10

NBSP = "\u00a0"
NARROW = "\u202f"
MONTHS = (
    "janvier février mars avril mai juin juillet août septembre octobre novembre décembre"
).split()


def number(value, precision=1, *, fixed=False):
    value = float(value)
    if not isfinite(value):
        raise ValueError("A displayed number must be finite")
    rendered = f"{value:,.{max(0, precision)}f}"
    if precision and not fixed:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered.replace(",", NARROW).replace(".", ",")


def rounded(value, precision=None):
    value = float(value)
    if precision is None:
        precision = 2 - floor(log10(abs(value))) if value else 0
    return number(round(value, precision), max(0, precision))


def scale_word(word, shown):
    """French agreement: `1,6 million`, `2,0 millions` (plural from two)."""
    value = float(shown.replace(NARROW, "").replace(",", "."))
    return word + ("s" if abs(value) >= 2 else "")


def quantity(value, unit="", precision=None, compact=False):
    value = float(value)
    if unit == "%":
        return number(value, 1 if precision is None else precision) + NARROW + "%"
    if abs(value) >= 1e9:
        label = "Md" if compact else scale_word("milliard", rounded(value / 1e9))
        result = rounded(value / 1e9) + NBSP + label
    elif abs(value) >= 1e6:
        label = "M" if compact else scale_word("million", number(value / 1e6, 1, fixed=True))
        result = number(value / 1e6, 1, fixed=True) + NBSP + label
    else:
        result = rounded(value, precision)
    if unit:
        unit = "d’habitants" if unit == "habitants" and abs(value) >= 1e6 and not compact else unit
        result += NBSP + unit
    return result


def record(item, *, compact=False):
    return quantity(item["value"], item.get("unit", ""), item.get("precision"), compact)


def date_fr(value):
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return f"{value.day} {MONTHS[value.month - 1]} {value.year}"


def euro(value, unit, fx):
    """Approximate euro equivalent of a local-currency amount at the fiche's stored rate.

    `fx` is the fiche's `euro` record: `currency` (ISO code), `per_euro` (units of local
    currency for one euro, annual average) and `year`. The unit keeps its suffix:
    `TWD/mois` becomes `€/mois`.
    """
    code = fx["currency"]
    if not unit.startswith(code):
        raise ValueError(f"Euro conversion expects an amount in {code}, got {unit!r}")
    rate = float(fx["per_euro"])
    if not isfinite(rate) or rate <= 0:
        raise ValueError("The euro rate must be a positive number")
    return quantity(float(value) / rate, "€" + unit[len(code) :])


def with_euro(rendered, value, unit, fx):
    """`50 600 TWD` followed by its approximate euro value in parentheses."""
    return f"{rendered} (≈{NBSP}{euro(value, unit, fx)})"
