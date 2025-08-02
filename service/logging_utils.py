# service/logging_utils.py
from fastapi import Request
from sqlalchemy.orm import Session

from models.visit_log import VisitLog


def log_visit(request: Request, db: Session):
    ip_address = request.headers.get("x-real-ip") or request.client.host
    visit = VisitLog(
        path=request.url.path,
        method=request.method,
        ip_address=ip_address,
    )
    db.add(visit)
    db.commit()
