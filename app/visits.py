# app/visits.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db.session import get_db
from models.visit_log import VisitLog

router = APIRouter()


def log_visit(request: Request, db: Session) -> int:
    ip_address = (
        request.client.host if request.client and request.client.host else "unknown"
    )
    visit = VisitLog(
        path=request.url.path, method=request.method, ip_address=ip_address
    )
    db.add(visit)
    db.commit()
    # db.refresh(visit)

    # Возвращает общее количество визитов
    return db.query(VisitLog).count()


@router.get("/visits", tags=["Visits"])
async def get_visits(request: Request, db: Session = Depends(get_db)) -> dict:
    total_visits = log_visit(request, db)
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
