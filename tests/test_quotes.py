# tests/test_quotes.py
import pytest

from service.service import quotes_storage

test_quotes_data = [
    {"ID": 0, "author": "Pytest", "text": "Тестируй что бы не было багов, AUF"},
    {"ID": 1, "author": "Другой", "text": "Цитата 2(1)"},
    {"ID": 2, "author": "Шлёпа", "text": "Если тебе было весело, то нечего сожалеть."},
    {
        "ID": 3,
        "author": "Шлёпа",
        "text": "Пельмени это очень вкусно. Рецепт простой: много мяса мало теста",
    },
]


@pytest.fixture
def mock_quotes(monkeypatch):
    def _mock(data):
        monkeypatch.setattr(quotes_storage, "get_all", lambda force_refresh=False: data)

    return _mock


# 1. Получение рандомной цитаты из мока
@pytest.mark.asyncio
async def test_random_quote_success(client, mock_quotes):
    mock_quotes(test_quotes_data)
    response = await client.get("/api/quotes/random?nocache=true")
    json_data = response.json()["quotes"]

    assert response.status_code == 200
    assert json_data in test_quotes_data


# 2. Получение всех цитат
@pytest.mark.asyncio
async def test_get_all_quotes(client, mock_quotes):
    mock_quotes(test_quotes_data)
    response = await client.get("/api/quotes?nocache=true")
    json_data = response.json()["quotes"]

    assert response.status_code == 200
    assert json_data == test_quotes_data


# 3. Получаем цитату по ID
@pytest.mark.asyncio
async def test_get_quote_by_ID(client, mock_quotes):
    mock_quotes(test_quotes_data)
    response = await client.get("/api/quotes/1?nocache=true")
    json_data = response.json()["quotes"]

    assert response.status_code == 200
    assert json_data["ID"] == 1


# 4. Получаем цитату по автору
@pytest.mark.asyncio
async def test_get_quote_by_author(client, mock_quotes):
    mock_quotes(test_quotes_data)
    response = await client.get("/api/quotes/search?nocache=true&author=Шлёпа")
    json_data = response.json()["quotes"]
    assert response.status_code == 200
    assert all("Шлёпа" in quote["author"] for quote in json_data)


# 5. Проверка ошибок получения цитаты
@pytest.mark.asyncio
async def test_error_get_quote(client, mock_quotes):
    mock_quotes(test_quotes_data)
    response = await client.get("/api/quotes/search?nocache=true&author=Неизвестный")
    assert response.status_code == 404
    assert response.json()["detail"] == {"error": "Цитаты не найдены."}

    response = await client.get("/api/quotes/999?nocache=true")
    assert response.status_code == 404
    assert response.json()["detail"] == {"error": "Цитаты не найдены."}


# 6. Проверка ошибки получения всех цитат
@pytest.mark.asyncio
async def test_error_get_all_quotes(client, mock_quotes):
    mock_quotes([])
    response = await client.get("/api/quotes?nocache=true")

    assert response.status_code == 404
    assert response.json()["detail"] == {"error": "Цитаты не найдены."}
