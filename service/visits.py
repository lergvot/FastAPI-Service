# service/visits.py
from fastapi import Request
from sqlalchemy.orm import Session

from models.visit_log import VisitLog


def log_visit(request: Request, db: Session) -> int:
    ip_address = (
        request.client.host if request.client and request.client.host else "unknown"
    )
    visit = VisitLog(
        path=request.url.path, method=request.method, ip_address=ip_address
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)

    # Возвращает общее количество визитов
    return db.query(VisitLog).count()
