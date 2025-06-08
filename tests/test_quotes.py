# tests/test_quotes.py
from unittest.mock import MagicMock, patch

import pytest
import respx
from fastapi import Request
from starlette.datastructures import QueryParams

from app.quotes import get_random_quote
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


# 1. Получение рандомной цитаты из мока
@pytest.mark.asyncio
async def test_random_quote_success(client, monkeypatch):
    monkeypatch.setattr(
        quotes_storage, "get_all", lambda force_refresh=False: test_quotes_data
    )

    response = await client.get("/api/quotes/random?nocache=true")
    json_data = response.json()["quotes"]

    assert response.status_code == 200
    assert json_data in test_quotes_data


# 2. Получение всех цитат
@pytest.mark.asyncio
async def test_get_all_quotes(client, monkeypatch):
    monkeypatch.setattr(
        quotes_storage, "get_all", lambda force_refresh=False: test_quotes_data
    )

    response = await client.get("/api/quotes?nocache=true")
    json_data = response.json()["quotes"]

    assert response.status_code == 200
    assert json_data == test_quotes_data
