import pytest
from httpx import AsyncClient
from main import app  # путь к твоему FastAPI-приложению


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
