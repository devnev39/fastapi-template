import logging

from datetime import datetime
from datetime import timezone
from logging.handlers import SysLogHandler

import structlog

from src.config.settings import settings

logging.getLogger().setLevel(logging.CRITICAL)

app_logger = logging.getLogger("applogger")
debug_logger = logging.getLogger("debuglogger")

app_logger_level = settings.APP_LOGGER_LEVEL
app_logger.setLevel(app_logger_level)
debug_logger.setLevel(app_logger_level)

# First bind the local stdout logger to stream the output

console_handler = logging.StreamHandler()
console_handler.setLevel(app_logger_level)


file_handler = logging.FileHandler(
    f"{datetime.strftime(datetime.now(timezone.utc), '%Y_%m_%d')}.log"
)

app_logger.addHandler(console_handler)
app_logger.addHandler(file_handler)
debug_logger.addHandler(console_handler)

if settings.APP_LOGGER_ADDRESS is None:
    app_logger.warning("App logger address not set. Syslog will not be enabled.")
elif settings.APP_LOGGER_ADDRESS and settings.APP_LOGGER_PORT:
    web_handler = SysLogHandler(
        address=(settings.APP_LOGGER_ADDRESS, settings.APP_LOGGER_PORT)
    )
    web_handler.setLevel(app_logger_level)
    app_logger.addHandler(web_handler)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME]
        ),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger("applogger")
