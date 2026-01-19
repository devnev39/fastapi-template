import functools
import inspect
import time
from contextlib import contextmanager

from src.core.logger.context import span_list


@contextmanager
def create_span(name: str | None = None):
    start = time.perf_counter()
    yield
    period = time.perf_counter() - start
    prev_list = span_list.get() if span_list.get() else []
    prev_list.append({"name": name, "time": round(period * 1000, 2)})
    span_list.set(prev_list)


def monitor(arg):
    if callable(arg):
        # arg is a function
        # check if coroutine or function
        if inspect.iscoroutinefunction(arg):

            @functools.wraps(arg)
            async def wrapper(*args, **kwargs):
                with create_span(arg.__name__):
                    return await arg(*args, **kwargs)

            return wrapper

        @functools.wraps(arg)
        def wrapper(*args, **kwargs):
            with create_span(arg.__name__):
                return arg(*args, **kwargs)

        return wrapper
    # arg is name
    # check function type
    def inner_wrapper(func):
        # check func type
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                with create_span(arg):
                    return await func(*args, **kwargs)

            return wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with create_span(arg):
                return func(*args, **kwargs)

        return wrapper

    return inner_wrapper
