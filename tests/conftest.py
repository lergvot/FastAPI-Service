# tests/conftest.py
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient

from main import app


@pytest_asyncio.fixture
async def client():
    # Явно запускаем lifecycle-прослойку (lifespan), чтобы инициализировать кэш и прочее
    async with LifespanManager(app):
        backend = InMemoryBackend()
        await FastAPICache.clear()
        FastAPICache.init(backend)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture(autouse=True)
def log_separator(request):
    """Добавляет разделители вокруг тестов и управляет уровнем логирования"""
    print(f"\n")
    yield
    print(f"\n{'-'*80}")


# Хук для декодирования кириллицы в id параметров тестов
def pytest_itemcollected(item):
    """Декодирует кириллические id параметров тестов"""
    if "[" in item.name and "\\u" in item.name:
        try:
            decoded = item.name.encode().decode("unicode_escape")
            item._nodeid = decoded
        except Exception:
            pass  # Не мешаем сборке, если что-то пойдет не так
