from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.deps import get_today
from app.main import app
from app.store import store

TODAY = date(2026, 3, 2)


@pytest.fixture
def today():
    """Mutable clock: tests set `today.value` to move time."""

    class Clock:
        value = TODAY

    clock = Clock()
    app.dependency_overrides[get_today] = lambda: clock.value
    yield clock
    app.dependency_overrides.clear()


@pytest.fixture
def client(today):
    with TestClient(app) as c:
        store.seed()
        yield c
