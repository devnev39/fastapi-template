from datetime import datetime

from pydantic import BaseModel

from src.core.utils.time import get_utc_now


class CreatedAtProps(BaseModel):
    created_by: str | None = None
    created_at: datetime = get_utc_now()


class UpdatedAtProps(BaseModel):
    updated_at: datetime = get_utc_now()
    updated_by: str | None = None


class StatusResponse(BaseModel):
    status: str = "Running"
