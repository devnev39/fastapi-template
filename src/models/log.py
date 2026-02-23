from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Log(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(True), nullable=False)
    pathname: Mapped[str] = mapped_column(String, nullable=False)
    event: Mapped[str] = mapped_column(String, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=True)
    extra_str: Mapped[str] = mapped_column(String, nullable=True)
    spans: Mapped[list] = mapped_column(JSONB, nullable=True)
    error: Mapped[str] = mapped_column(String, nullable=True)
    method: Mapped[str] = mapped_column(String, nullable=True)
    request_id: Mapped[str] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(String, nullable=True)
    latency: Mapped[str] = mapped_column(Float, nullable=True)
