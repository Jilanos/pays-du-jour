"""Validate fiche rendering and warn about duplicated reading metrics.

Run from the repository: uv run python scripts/lint_fiche.py [TWN ...]
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings  # noqa: E402
from app.content import CITATION, read_fiche  # noqa: E402
from app.format import record  # noqa: E402


def lint(code, settings):
    folder = settings.content_dir / code
    body = (folder / "fiche.md").read_text().split("---", 2)[2]
    data = json.loads((folder / "data.json").read_text())
    errors, warnings = [], []
    if body.count("{{sources}}") != 1:
        errors.append("Exactly one final {{sources}} block is required")
    if re.search(r"\[S\d+|—", body):
        errors.append("Inline source IDs or em dashes in reading prose")
    plain = "\n".join(CITATION.sub("", line) for line in body.splitlines())
    plain += "\n" + "\n".join(c.get("note_visible", "") for c in data.get("charts", []))
    for item in data.get("keyfacts", []) + data.get("indices", []):
        if not isinstance(item["value"], (int, float)):
            errors.append(f"{item['id']}: value must be numeric")
            continue
        candidates = (str(item["value"]), record(item))
        if any(re.search(r"(?<![\d.,])" + re.escape(v) + r"(?![\d.,])", plain) for v in candidates):
            warnings.append(f"{item['id']}: metric repeated in prose or visible chart note")
        for key, rec in data.get("prose_values", {}).items():
            if rec["value"] == item["value"] and "{{value:" + key + "}}" in body:
                warnings.append(f"{item['id']}: prose record {key} repeats the metric")
    try:
        read_fiche(code, settings)
    except (ValueError, KeyError) as exc:
        errors.append(str(exc))
    for label, findings in (("ERROR", errors), ("WARN", warnings)):
        for finding in findings:
            print(f"{label} {code}: {finding}")
    if not errors and not warnings:
        print(f"OK {code}: contract, citations and metric ownership")
    return len(errors)


if __name__ == "__main__":
    config = Settings()
    codes = sys.argv[1:] or sorted(p.name for p in config.content_dir.iterdir() if p.is_dir())
    sys.exit(bool(sum(lint(code, config) for code in codes)))
