# models/visit_log.py
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from db.base import Base  # путь зависит от твоей структуры


class VisitLog(Base):
    __tablename__ = "visit_log"

    id = Column(Integer, primary_key=True, index=True)
    visited_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 поддержка
