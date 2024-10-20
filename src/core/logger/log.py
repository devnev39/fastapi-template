import logging
from datetime import datetime
from typing import Optional
from fastapi import Request
from pydantic import BaseModel

from src.config.settings import settings

logging.getLogger().setLevel(logging.CRITICAL)

app_logger = logging.getLogger("applogger")

app_logger_level = settings.APP_LOGGER_LEVEL
app_logger.setLevel(app_logger_level)

# First bind the local stdout logger to stream the output

console_handler = logging.StreamHandler()
console_handler.setLevel(app_logger_level)

app_logger.addHandler(console_handler)

if settings.APP_LOGGER_ADDRESS is None:
    app_logger.warning("App logger address not set. Syslog will not be enabled.")
else:
    web_handler = logging.handlers.SysLogHandler(
        address=(settings.APP_LOGGER_ADDRESS, settings.APP_LOGGER_PORT)
    )
    web_handler.setLevel(app_logger_level)
    app_logger.addHandler(web_handler)


class AppLog(BaseModel):
    error: Optional[str] = None
    msg: Optional[str] = None
    trace_id: str = str(datetime.now().timestamp())
    timestamp: str = datetime.now().isoformat()
    filename: Optional[str] = None
    extra: Optional[str] = None
    event: Optional[str] = None

    def update(self, log):
        dump = log.model_dump(exclude_none=True)
        self.__dict__.update(dump)
        self.timestamp = datetime.now().isoformat()
        self.trace_id = str(datetime.now().timestamp())


class Log(AppLog):
    device: Optional[str] = None
    url: Optional[str] = None
    addr: Optional[str] = None
    method: Optional[str] = None
    code: Optional[int] = 200
    payload: Optional[dict] = None
    level: Optional[str] = "DEBUG"
    status: Optional[str] = None
    user: Optional[str] = None


def get_log(request: Request) -> Log:
    return Log(
        device=request.headers.get("User-Agent", "Unknown"),
        url=request.url.path,
        method=request.method,
        addr=request.client.host,
    )
