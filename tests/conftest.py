# tests/conftest.py
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from asgi_lifespan import LifespanManager
from fastapi_cache import FastAPICache


@pytest_asyncio.fixture
async def client():
    # Явно запускаем lifecycle-прослойку (lifespan), чтобы инициализировать кэш и прочее
    async with LifespanManager(app):
        await FastAPICache.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
