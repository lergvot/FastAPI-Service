# tests/test_main.py
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_status_code():
    pass
