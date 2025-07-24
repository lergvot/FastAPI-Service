# service/visits.py
from fastapi import Request
from sqlalchemy.orm import Session

from models.visit_log import VisitLog


def log_visit(request: Request, db: Session) -> int:
    visit = VisitLog(
        path=request.url.path, method=request.method, ip_address=request.client.host
    )
    db.add(visit)
    db.commit()

    # Возвращает общее количество визитов
    return db.query(VisitLog).count()
