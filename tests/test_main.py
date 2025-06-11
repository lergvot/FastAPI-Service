# tests/test_main.py
import httpx
import pytest
import respx
from httpx import Response

from main import fetch_data


# 1. Проверка моками роутов на главной странице
@respx.mock
@pytest.mark.asyncio
async def test_index_route(client):
    respx.get("/api/weather").mock(
        return_value=Response(
            200, json={"weather": {"current_weather": {"weather_text": "Пасмурно"}}}
        )
    )
    respx.get("/api/cat").mock(
        return_value=Response(200, json={"cat": {"url": "https://kotik.jpg"}})
    )
    respx.get("/api/quotes/random").mock(
        return_value=Response(200, json={"quotes": {"text": "AUF"}})
    )
    respx.get("/api/notes").mock(
        return_value=Response(200, json={"notes": ["заметка1", "заметка2"]})
    )
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AUF" in response.text
    assert "Пасмурно" in response.text
    assert "https://kotik.jpg" in response.text
    assert "заметка1" in response.text
    assert "<title>Личный дашборд FastAPI</title>" in response.text


# 2. Проверка доступности страницы about и ресурсов
@respx.mock
@pytest.mark.asyncio
async def test_about_page(client):
    response = await client.get("/about.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Важная информация</title>" in response.text


# 3. Обработка ошибки запроса (fetch_data возвращает None)
@pytest.fixture
def mock_fetch_data(monkeypatch):
    async def mocked(*args, **kwargs):
        return None

    monkeypatch.setattr("main.fetch_data", mocked)


@pytest.mark.asyncio
async def test_fetch_data_handles_error(monkeypatch):
    async def mock_httpx(*args, **kwargs):
        raise httpx.ConnectError("Fail")

    monkeypatch.setattr("httpx.AsyncClient.get", mock_httpx)
    result = await fetch_data("https://fail.test")
    assert result is None


# 4. Обработка query параметра ?error=...
@respx.mock
@pytest.mark.asyncio
async def test_query_error_parameter(client):
    respx.get("/api/weather").mock(
        return_value=Response(
            200, json={"weather": {"current_weather": {"weather_text": "Пасмурно"}}}
        )
    )
    respx.get("/api/cat").mock(
        return_value=Response(200, json={"cat": {"url": "https://kotik.jpg"}})
    )
    respx.get("/api/quotes/random").mock(
        return_value=Response(200, json={"quotes": {"text": "AUF"}})
    )
    respx.get("/api/notes").mock(
        return_value=Response(200, json={"notes": ["заметка1", "заметка2"]})
    )
    response = await client.get("/?error=ошибка123")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AUF" in response.text
    assert "Пасмурно" in response.text
    assert "https://kotik.jpg" in response.text
    assert "заметка1" in response.text
    assert "ошибка123" in response.text


# 5. /static путь доступен
@respx.mock
@pytest.mark.asyncio
async def test_static_resources(client):
    response = await client.get("/static/info.mp4")
    assert response.status_code == 200
    assert "video/mp4" in response.headers["content-type"]

    response = await client.get("/static/cat_fallback.gif")
    assert response.status_code == 200
    assert "image/gif" in response.headers["content-type"]

    response = await client.get("/static/favicon.svg")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers["content-type"]

    response = await client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


# 6. Проверка функции fetch_data (успешный запрос)
@respx.mock
@pytest.mark.asyncio
async def test_fetch_data_success():
    url = "https://some.api"
    respx.get(url).mock(return_value=Response(200, json={"result": "ok"}))
    data = await fetch_data(url)
    assert data == {"result": "ok"}
    assert isinstance(data, dict)
