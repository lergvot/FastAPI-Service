# tests/test_cat.py
import pytest
import respx
from httpx import Response

from service.variables import CAT_FALLBACK


# 1. Успешный случай с моками
@respx.mock
@pytest.mark.asyncio
async def test_api_cat_success(client):
    mock_url = "https://cdn.fakecat.com/cat.jpg"
    api_mock = respx.get("https://api.thecatapi.com/v1/images/search").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "abc123",
                    "url": mock_url,
                    "width": 800,
                    "height": 600,
                }
            ],
        )
    )

    response = await client.get("/api/cat?nocache=true")
    data = response.json()

    assert api_mock.called, "API не был вызван!"
    assert response.status_code == 200
    assert data["cat"]["url"] == mock_url


# 2. Проверка локального fallback-файла
@pytest.mark.asyncio
async def test_static_fallback_image(client):
    response = await client.get(CAT_FALLBACK["url"])

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


# 3. Fallback при ошибке API
@respx.mock
@pytest.mark.asyncio
async def test_api_cat_fallback_on_error(client):
    respx.get("https://api.thecatapi.com/v1/images/search").mock(
        return_value=Response(500)
    )

    response = await client.get("/api/cat?nocache=true")
    data = response.json()

    assert response.status_code == 200
    assert data["cat"] == CAT_FALLBACK
    assert data["status"] == "fallback"


# Пример использования времени жизни кэша для тестов
# @cached_route("cat_cache", ttl=2)  # кэш будет жить 2 секунды только для этого теста
