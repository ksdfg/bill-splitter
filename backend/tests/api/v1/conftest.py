from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
