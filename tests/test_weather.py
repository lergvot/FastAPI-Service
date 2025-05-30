# tests/test_weather.py
from datetime import datetime, timezone

import pytest
import respx
from fastapi import status
from httpx import Response

from app.weather import (
    to_moscow_time,
    weather_code_to_text,
    wind_direction_to_text,
)
from service.variables import WEATHER_FALLBACK, latitude, longitude

api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
mock_data = {
    "latitude": 55.75,
    "longitude": 37.625,
    "generationtime_ms": 0.0412464141845703,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 152,
    "current_weather_units": {
        "time": "iso8601",
        "interval": "seconds",
        "temperature": "°C",
        "windspeed": "km/h",
        "winddirection": "°",
        "is_day": "",
        "weathercode": "wmo code",
    },
    "current_weather": {
        "time": "2025-05-28T12:00",
        "interval": 900,
        "temperature": 27.4,
        "windspeed": 13.7,
        "winddirection": 180,
        "is_day": 1,
        "weathercode": 0,
    },
}


# Фикстура для заморозки времени
@pytest.fixture
def freeze_time(monkeypatch):
    class FrozenTime:
        @classmethod
        def now(cls, tz=None):
            return datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    monkeypatch.setattr("datetime.datetime", FrozenTime)


# 1. Тест успешного получения данных с API
@respx.mock
@pytest.mark.asyncio
async def test_get_weather_success(client):

    # Мокаем API-запрос

    respx.get(api_url).mock(return_value=Response(200, json=mock_data))

    response = await client.get("api/weather?nocache=true")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["current_weather"]["wind_direction"] == "Южный"
    assert data["current_weather"]["moscow_time"] == "15:00"


# 2. Тест получения данных из кэша
@respx.mock
@pytest.mark.asyncio
async def test_weather_caching(client):

    mock = respx.get(api_url).mock(
        return_value=Response(
            200,
            json=mock_data,
        )
    )
    await client.get("api/weather?nocache=true")
    assert mock.call_count == 1, "Вызов API без кэша"

    await client.get("api/weather")
    assert (
        mock.call_count == 1
    ), f"Второй вызов должен использовать кэш {mock.call_count}"


# 3. Тест отработки заглушки при отсутствии данных в кэше
@respx.mock
@pytest.mark.asyncio
async def test_weather_fallback(client):
    respx.get(api_url).mock(return_value=Response(500))

    response = await client.get("api/weather?nocache=true")
    assert response.status_code == 200
    assert response.json() == WEATHER_FALLBACK


# 4. Тест обработки случая, когда текущая погода отсутствует в ответе API
@respx.mock
@pytest.mark.asyncio
async def test_weather_api_no_current_weather(client):
    broken_mock_data = {k: v for k, v in mock_data.items() if k != "current_weather"}

    respx.get(api_url).mock(return_value=Response(200, json=broken_mock_data))

    response = await client.get("api/weather?nocache=true")
    assert response.status_code == 200
    assert response.json() == WEATHER_FALLBACK


# 5. Тест конвертации градусов ветра в текстовое описание
@pytest.mark.parametrize(
    "degrees, expected",
    [
        (-360, "Северный"),
        (0, "Северный"),
        (11.25, "Северо-северо-восточный"),
        (90, "Восточный"),
        (180, "Южный"),
        (200, "Юго-юго-западный"),
        (215, "Юго-западный"),
        (348.74, "Северо-северо-западный"),
        (348.75, "Северный"),
        (350, "Северный"),
        (360, "Северный"),
    ],
)
def test_wind_direction_conversion(degrees, expected):
    assert wind_direction_to_text(degrees) == expected


# 6. Тест конвертации кода погоды в текстовое описание
@pytest.mark.parametrize(
    "code, expected",
    [
        (0, "Ясно"),
        (95, "Гроза"),
        (100, "Неизвестный код: (100)"),
    ],
)
def test_weather_code_conversion(code, expected):
    assert weather_code_to_text(code) == expected


# 7. Тест конвертации времени в московское время
def test_moscow_time_conversion():
    assert to_moscow_time("2024-01-01T09:00+00:00") == "12:00"
