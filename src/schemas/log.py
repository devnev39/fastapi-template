from datetime import datetime

from pydantic import BaseModel


class Log(BaseModel):
    level: str
    timestamp: datetime
    pathname: str
    event: str | None = None
    status_code: int | None = None
    extra_str: str | None = None
    spans: list | None = None
    error: str | None = None
    method: str | None = None
    request_id: str | None = None
    path: str | None = None
    latency: float | None = None
