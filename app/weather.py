from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import time
from variables import *
import logging

logging.basicConfig(level=logging.INFO)
router = APIRouter()

class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float
    wind_direction: str  # Заменяем winddirection на текстовое представление
    weather_text: str    # Заменяем weathercode на текстовое описание
    is_day: int
    moscow_time: str     # Заменяем исходное время на московское

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_weather: CurrentWeather

weather_cache = None
next_update_time = None

def calculate_next_update(api_time_str: str) -> datetime:
    api_time = datetime.fromisoformat(api_time_str.replace("Z", "+00:00"))
    next_update = api_time + timedelta(minutes=15)
    return next_update.replace(tzinfo=timezone.utc)

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
        "Северо-северо-западный"
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
        99: "Гроза с сильным градом"
    }
    return codes.get(code, f"Неизвестный код: ({code})")

def to_moscow_time(iso_time: str) -> str:
    dt = datetime.fromisoformat(iso_time)
    moscow_dt = dt.replace(tzinfo=timezone.utc) + timedelta(hours=3)
    return moscow_dt.strftime("%H:%M")

async def fetch_weather() -> WeatherResponse:
    global weather_cache, next_update_time
    
    if next_update_time and datetime.now(timezone.utc) < next_update_time and weather_cache:
        logging.info("✅ Возвращаем кэшированные данные")
        return weather_cache

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            raw_weather = data["current_weather"]
            
            # Создаем новый объект с преобразованными данными
            processed_weather = {
                "temperature": raw_weather["temperature"],
                "windspeed": raw_weather["windspeed"],
                "wind_direction": wind_direction_to_text(raw_weather["winddirection"]),
                "weather_text": weather_code_to_text(raw_weather["weathercode"]),
                "is_day": raw_weather["is_day"],
                "moscow_time": to_moscow_time(raw_weather["time"])
            }
            
            api_update_time = raw_weather["time"]
            next_update_time = calculate_next_update(api_update_time)
            
            weather_data = WeatherResponse(
                latitude=data["latitude"],
                longitude=data["longitude"],
                generationtime_ms=data["generationtime_ms"],
                utc_offset_seconds=data["utc_offset_seconds"],
                timezone=data["timezone"],
                timezone_abbreviation=data["timezone_abbreviation"],
                elevation=data["elevation"],
                current_weather=CurrentWeather(**processed_weather)
            )
            
            weather_cache = weather_data
            return weather_data
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/weather", response_model=WeatherResponse)
async def get_weather():
    try:
        return await fetch_weather()
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка")
    