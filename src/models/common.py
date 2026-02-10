from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column

from src.core.utils.time import get_utc_now


class Timestamp:
    created_at: Annotated[datetime, mapped_column(DateTime, default=get_utc_now)]
    updated_at: Annotated[datetime, mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)]


class Creation:
    created_by: Annotated[str, mapped_column(String)]
    updated_by: Annotated[str, mapped_column(String)]
