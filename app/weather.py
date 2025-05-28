# app/weather.py
import httpx
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from fastapi_cache import FastAPICache
from service.variables import latitude, longitude, WEATHER_FALLBACK

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


def calculate_next_update(last_update_iso: str) -> datetime:
    last_update = datetime.fromisoformat(last_update_iso.replace("Z", "+00:00"))
    minute = (last_update.minute // 15 + 1) * 15
    if minute == 60:
        next_update = last_update.replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(hours=1)
    else:
        next_update = last_update.replace(minute=minute, second=0, microsecond=0)
    return next_update.astimezone(timezone.utc)


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
        logging.error(f"Ошибка API: {e}")
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении погоды: {e}")
        return None


@router.get("/weather", response_model=None, tags=["Weather"])
@router.get("/weather?nocache=true", response_model=None, tags=["Service"])
async def weather(request: Request) -> Dict[str, Any]:
    use_cache = request.query_params.get("nocache") != "true"
    cache_key = "weather_cache"
    backend = FastAPICache.get_backend()

    if use_cache and backend:
        cached_data = await backend.get(cache_key)
        if cached_data:
            try:
                # Проверяем, пора ли обновлять кэш
                last_iso = cached_data["current_weather"]["moscow_time"]
                last_update = datetime.strptime(last_iso, "%H:%M").replace(
                    year=datetime.utcnow().year,
                    month=datetime.utcnow().month,
                    day=datetime.utcnow().day,
                    tzinfo=timezone.utc,
                ) - timedelta(
                    hours=3
                )  # обратно из Москвы в UTC

                now_utc = datetime.now(timezone.utc)
                next_update = calculate_next_update(
                    last_update.isoformat().replace("+00:00", "Z")
                )
                if now_utc < next_update:
                    logging.info("✅ Возвращаем кэшированную погоду")
                    return cached_data
                else:
                    logging.info("♻️ Кэш устарел, получаем новые данные")
            except Exception as e:
                logging.warning(f"⚠️ Ошибка при проверке актуальности кэша: {e}")

    # Получаем свежую погоду
    weather_data = await fetch_weather()
    if not weather_data:
        logging.warning("☑️ Используем заглушку для погоды")
        return WEATHER_FALLBACK

    result = weather_data.dict()

    if use_cache and backend:
        try:
            # Расчёт TTL до следующего 15-минутного слота
            now = datetime.now(timezone.utc)
            next_update = calculate_next_update(now.isoformat())
            ttl = int((next_update - now).total_seconds())
            await backend.set(cache_key, result, expire=ttl)
            logging.info(f"Кэш обновлён, TTL = {ttl} сек")
        except Exception as e:
            logging.warning(f"⚠️ Не удалось сохранить в кэш: {e}")

    return result
