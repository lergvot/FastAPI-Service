# app/weather.py
import logging
from datetime import datetime, timedelta, timezone
from venv import logger

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from service.decorators import cached_route
from service.variables import WEATHER_FALLBACK, latitude, longitude

logger = logging.getLogger(__name__)
router = APIRouter()


class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float
    wind_direction: str
    weather_text: str
    is_day: int
    moscow_time: str


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_weather: CurrentWeather


def wind_direction_to_text(degrees: float) -> str:
    directions = [
        "Северный",
        "Северо-северо-восточный",
        "Северо-восточный",
        "Восточно-северо-восточный",
        "Восточный",
        "Восточно-юго-восточный",
        "Юго-восточный",
        "Юго-юго-восточный",
        "Южный",
        "Юго-юго-западный",
        "Юго-западный",
        "Западно-юго-западный",
        "Западный",
        "Западно-северо-западный",
        "Северо-западный",
        "Северо-северо-западный",
    ]
    idx = int((degrees + 11.25) % 360 / 22.5)
    return directions[idx]


def weather_code_to_text(code: int) -> str:
    codes = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Иней",
        51: "Морось слабая",
        53: "Морось",
        55: "Морось сильная",
        56: "Лёгкий ледяной дождь",
        57: "Ледяной дождь",
        61: "Дождь слабый",
        63: "Дождь",
        65: "Дождь сильный",
        66: "Лёгкий ледяной дождь",
        67: "Ледяной дождь",
        71: "Снег слабый",
        73: "Снег",
        75: "Снег сильный",
        77: "Снежные зерна",
        80: "Ливень слабый",
        81: "Ливень",
        82: "Ливень сильный",
        85: "Снегопад слабый",
        86: "Снегопад сильный",
        95: "Гроза",
        96: "Гроза с градом",
        99: "Гроза с сильным градом",
    }
    return codes.get(code, f"Неизвестный код: ({code})")


def to_moscow_time(iso_time: str) -> str:
    dt = datetime.fromisoformat(iso_time)
    moscow_dt = dt.replace(tzinfo=timezone.utc) + timedelta(hours=3)
    return moscow_dt.strftime("%H:%M")


async def fetch_weather() -> WeatherResponse | None:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            raw_weather = data["current_weather"]

            processed_weather = {
                "temperature": raw_weather["temperature"],
                "windspeed": raw_weather["windspeed"],
                "wind_direction": wind_direction_to_text(raw_weather["winddirection"]),
                "weather_text": weather_code_to_text(raw_weather["weathercode"]),
                "is_day": raw_weather["is_day"],
                "moscow_time": to_moscow_time(raw_weather["time"]),
            }

            return WeatherResponse(
                latitude=data["latitude"],
                longitude=data["longitude"],
                generationtime_ms=data["generationtime_ms"],
                utc_offset_seconds=data["utc_offset_seconds"],
                timezone=data["timezone"],
                timezone_abbreviation=data["timezone_abbreviation"],
                elevation=data["elevation"],
                current_weather=CurrentWeather(**processed_weather),
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка API: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении погоды: {e}")
        return None


@router.get("/weather", tags=["Weather"])
@router.get("/weather?nocache=true", tags=["Service"])
@cached_route("weather_cache", ttl=10, fallback_data=WEATHER_FALLBACK, source="weather")
async def weather(request: Request) -> dict:
    weather_data = await fetch_weather()
    if weather_data is None:
        return {"url": WEATHER_FALLBACK, "fallback": True}
    return weather_data.model_dump()
