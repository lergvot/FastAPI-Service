# tests/test_cache.py
import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from service.cache import delete_cached, get_cached, set_cached, ttl_logic


# 1. Проверка записи и чтения из кэша через set_cached и get_cached
@pytest.mark.asyncio
async def test_set_and_get_cached(monkeypatch):
    backend = InMemoryBackend()
    FastAPICache.init(backend)

    await set_cached("test:key", {"hello": "world"}, ttl=60)
    result = await get_cached("test:key")
    assert result == {"hello": "world"}


# 2. Проверка удаления ключа через delete_cached, если у backend есть метод .clear()
@pytest.mark.asyncio
async def test_delete_cached_with_clear(monkeypatch):
    backend = InMemoryBackend()
    FastAPICache.init(backend)

    await set_cached("test:key", {"hello": "world"}, ttl=60)
    await delete_cached("test:key")
    result = await get_cached("test:key")
    assert result is None  # ключ удалён


# 3. Проверка ttl_logic с weather-данными
def test_ttl_logic_weather():
    data = {"current_weather": {"temp": 22}}
    result = ttl_logic(data)
    assert isinstance(result, bool)


# 4. Проверка ttl_logic с данными от кота
def test_ttl_logic_cat():
    data = {"id": "abc", "url": "img.jpg", "width": 100, "height": 100}
    result = ttl_logic(data)
    assert isinstance(result, bool)


# 5. Проверка, что ttl_logic правильно возвращает TTL в секундах
def test_return_ttl():
    data = {"current_weather": {"temp": 22}}
    ttl = ttl_logic(data, return_ttl=True)
    assert isinstance(ttl, int)
    assert 1 <= ttl <= 900  # 15 минут = 900 сек (если weather)


# 6. Проверка поведения ttl_logic с неподдерживаемым source (или пустым словарём)
def test_ttl_logic_invalid_data():
    result = ttl_logic({}, source="auto")
    assert result is False


# 7. Кастомный backend без метода clear, чтобы проверить fallback-логику delete_cached
class MockBackendWithoutClear:
    def __init__(self):
        self._cache = {}

    async def set(self, key, value, expire):
        self._cache[key] = value

    async def get(self, key):
        return self._cache.get(key)


# 8. Проверка fallback-удаления ключа, если у backend нет метода clear
@pytest.mark.asyncio
async def test_delete_cached_fallback(monkeypatch):
    backend = MockBackendWithoutClear()
    FastAPICache.init(backend)

    await set_cached("x", {"a": 1}, ttl=60)
    await delete_cached("x")
    value = await get_cached("x")
    assert value is None or value == {}  # зависит от того, как backend возвращает None
