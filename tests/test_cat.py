import pytest
import respx
from httpx import Response
from variables import CAT_FALLBACK
from fastapi_cache import FastAPICache


# 1. Успешный случай с моками
@respx.mock
@pytest.mark.asyncio
@pytest.mark.category("cat")
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
    respx.get("https://api.thecatapi.com/v1/images/search").mock(
        return_value=Response(500)
    )

    response = await client.get("/api/cat?nocache=true")

    assert response.status_code == 200
    assert response.json()["url"] == CAT_FALLBACK
