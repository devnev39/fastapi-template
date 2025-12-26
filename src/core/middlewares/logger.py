import time
import uuid

from starlette.types import ASGIApp
from starlette.types import Message
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send
from structlog import contextvars

from src.core.logger.context import error
from src.core.logger.context import extra_str
from src.core.logger.context import request_id
from src.core.logger.log import logger


class LoggingASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        uid = str(uuid.uuid4())
        request_id.set(uid)
        contextvars.bind_contextvars(
            request_id=uid, method=scope.get("method"), path=scope.get("path")
        )

        try:
            contextvars.bind_contextvars(error=error.get(), extra_str=extra_str.get())
            logger.info(event="http.request.start", status_code=None)

            async def send_wrapper(message: Message) -> None:
                await send(message)
                if message.get("type") == "http.response.start":
                    contextvars.bind_contextvars(
                        error=error.get(), extra_str=extra_str.get()
                    )
                    req_time = time.perf_counter() - start
                    logger.info(
                        event="http.response.end",
                        latency=round(req_time * 1000, 2),
                        status_code=message.get("status"),
                    )

            await self.app(scope, receive, send_wrapper)
        except Exception as ex:
            logger.error(
                error=str(ex),
                event=ex.event if hasattr(ex, "event") else "app.middleware.error",
            )
            raise ex
