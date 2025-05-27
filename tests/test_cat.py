import pytest
import respx
from httpx import Response
from variables import CAT_FALLBACK
from fastapi_cache import FastAPICache


# 1. Успешный случай с моками
@respx.mock
@pytest.mark.asyncio
async def test_api_cat_success(client):
    mock_url = "https://cdn.fakecat.com/cat.jpg"
    api_mock = respx.get("https://api.thecatapi.com/v1/images/search").mock(
        return_value=Response(
            200,
            json=[{"id": "abc123", "url": mock_url, "width": 800, "height": 600}],
        )
    )

    response = await client.get("/api/cat")

    assert api_mock.called, "API не был вызван!"
    assert response.status_code == 200
    assert response.json()["url"] == mock_url


# 2. Проверка локального fallback-файла
@pytest.mark.asyncio
async def test_static_fallback_image(client):
    response = await client.get(CAT_FALLBACK)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


# 3. Fallback при ошибке API
@respx.mock
@pytest.mark.asyncio
async def test_api_cat_fallback_on_error(client):
    # Привязываем mock к тому же клиенту, что будет создан внутри get_cat()
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get("https://api.thecatapi.com/v1/images/search").mock(
            return_value=Response(500)
        )

        # Удаляем кэш перед запросом (вдруг остался от предыдущего)
        await FastAPICache.clear()

        response = await client.get("/api/cat")

        # Проверяем, был ли вызван наш mock
        assert any(route.called for route in respx_mock.routes), "Мок не был вызван!"
        assert response.status_code == 200
        assert response.json()["url"] == CAT_FALLBACK

        cached_data = await FastAPICache.get_backend().get("cat_cache")
        assert cached_data is not None
        assert cached_data["url"] == CAT_FALLBACK
