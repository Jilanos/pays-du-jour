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


def quantity(value, unit="", precision=None, compact=False):
    value = float(value)
    if unit == "%":
        return number(value, 1 if precision is None else precision) + NARROW + "%"
    if abs(value) >= 1e9:
        label = "Md" if compact else "milliards"
        result = rounded(value / 1e9) + NBSP + label
    elif abs(value) >= 1e6:
        label = "M" if compact else "millions"
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
