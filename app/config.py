"""Application configuration, independent of the working directory."""

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    content_dir: Path = field(
        default_factory=lambda: Path(os.getenv("PAYS_CONTENT_DIR", ROOT / "fiches"))
    )
    order_path: Path = field(
        default_factory=lambda: Path(os.getenv("PAYS_ORDER_PATH", ROOT / "data/ordre.csv"))
    )
    geo_dir: Path = field(
        default_factory=lambda: Path(os.getenv("PAYS_GEO_DIR", ROOT / "data/geo"))
    )
    database_path: Path = field(
        default_factory=lambda: Path(os.getenv("PAYS_DB_PATH", "/data/pays.sqlite3"))
    )
