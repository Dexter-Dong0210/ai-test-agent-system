"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from psycopg.errors import (
    ConnectionTimeout,
    InternalError,
    OperationalError,
    UndefinedTable,
)
from psycopg_pool.errors import PoolTimeout, TooManyRequests

P = ParamSpec("P")
T = TypeVar("T")

# pragma: no cover  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2WnpKbWNnPT06NzExNzA5ODc=

class RetryableException(Exception):
    pass


RETRIABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
    OperationalError,
    InternalError,
    RetryableException,
)
# pragma: no cover  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2WnpKbWNnPT06NzExNzA5ODc=

OVERLOADED_EXCEPTIONS: tuple[type[BaseException], ...] = (
    PoolTimeout,
    ConnectionTimeout,
    TooManyRequests,
)

# fmt: off  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2WnpKbWNnPT06NzExNzA5ODc=

def retry_db(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    attempts = 3

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        for i in range(attempts):
            if i == attempts - 1:
                return await func(*args, **kwargs)
            try:
                return await func(*args, **kwargs)
            except UndefinedTable:
                await asyncio.sleep(5)
            except RETRIABLE_EXCEPTIONS:
                await asyncio.sleep(0.01)

    return wrapper
