from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column, Mapped

from src.core.utils.time import get_utc_now


class Timestamp:
    created_at: Mapped[datetime] = mapped_column(DateTime(True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(True), default=get_utc_now, onupdate=get_utc_now)


class Creation:
    created_by: Mapped[str] = mapped_column(String)
    updated_by: Mapped[str] = mapped_column(String, nullable=True)
