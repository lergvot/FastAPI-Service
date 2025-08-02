# models/api_log.py
from sqlalchemy import Column, DateTime, Float, Integer, String, func

from db.base import Base


class APILog(Base):
    __tablename__ = "api_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
