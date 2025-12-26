from contextvars import ContextVar

exception_message = ContextVar("exception_name", default=None)
extra_str = ContextVar("extra_str", default=None)
request_id = ContextVar("request_id", default=None)
error = ContextVar("error", default=None)
