import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def settings():
    return Settings(content_dir=FIXTURES / "fiches")


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def charts():
    return json.loads((FIXTURES / "fiches/FRA/data.json").read_text())["charts"]
