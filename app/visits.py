# app/visits.py
"""
Модуль для отслеживания и анализа посещений API.

Предоставляет эндпоинты для получения статистики посещений, включая:
- Общее количество посещений
- Количество посещений за последние 24 часа
- Количество уникальных посетителей за последние 24 часа
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db.session import get_db
from models.visit_log import VisitLog

router = APIRouter()


@router.get("/visits", tags=["Visits"])
async def get_visits(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Получение статистики посещений.

    Args:
        request (Request): Объект запроса FastAPI
        db (Session): Сессия базы данных, внедряемая через FastAPI dependency

    Returns:
        dict: Словарь со статистикой посещений, содержащий:
            - total: общее количество посещений
            - last_24h: количество посещений за последние 24 часа
            - unique: количество уникальных посетителей за последние 24 часа

    Example:
        {
            "visits": {
                "total": 100,
                "last_24h": 25,
                "unique": 15
            },
            "status": "success"
        }
    """
    total_visits = db.query(VisitLog).count()
    last_day = datetime.now() - timedelta(days=1)
    last_day_count = db.query(VisitLog).filter(VisitLog.visited_at >= last_day).count()

    unique_visits = (
        db.query(VisitLog.ip_address)
        .filter(VisitLog.visited_at >= last_day)
        .distinct()
        .count()
    )

    return {
        "visits": {
            "total": total_visits,
            "last_24h": last_day_count,
            "unique": unique_visits,
        },
        "status": "success",
    }
