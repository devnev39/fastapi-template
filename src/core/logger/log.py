import logging
from logging.handlers import SysLogHandler
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
elif settings.APP_LOGGER_ADDRESS and settings.APP_LOGGER_PORT:
    web_handler = SysLogHandler(
        address=(settings.APP_LOGGER_ADDRESS, settings.APP_LOGGER_PORT)
    )
    web_handler.setLevel(app_logger_level)
    app_logger.addHandler(web_handler)
