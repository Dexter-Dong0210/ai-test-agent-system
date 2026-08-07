"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""
from __future__ import annotations

import asyncio
import functools
import typing
from collections import ChainMap
from contextvars import copy_context
from os import getenv
from typing import Any, ParamSpec, TypeVar

from langgraph.constants import CONF
from typing_extensions import TypedDict
# noqa  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2U1ZOV1Z3PT06M2I4ODk0ZGQ=

if typing.TYPE_CHECKING:
    from concurrent.futures import Executor

    from langchain_core.runnables import RunnableConfig

try:
    from langchain_core.runnables.config import (
        var_child_runnable_config,
    )
except ImportError:
    var_child_runnable_config = None  # type: ignore[invalid-assignment]

CONFIG_KEYS = [
    "tags",
    "metadata",
    "callbacks",
    "run_name",
    "max_concurrency",
    "recursion_limit",
    "configurable",
    "run_id",
]

COPIABLE_KEYS = [
    "tags",
    "metadata",
    "callbacks",
    "configurable",
]

DEFAULT_RECURSION_LIMIT = int(getenv("LANGGRAPH_DEFAULT_RECURSION_LIMIT", "25"))

T = TypeVar("T")
P = ParamSpec("P")
# fmt: off  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2U1ZOV1Z3PT06M2I4ODk0ZGQ=


def _is_not_empty(value: Any) -> bool:
    if isinstance(value, list | tuple | dict):
        return len(value) > 0
    else:
        return value is not None


class _Config(TypedDict):
    tags: list[str]
    metadata: ChainMap
    callbacks: None
    recursion_limit: int
    configurable: dict[str, Any]
# fmt: off  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2U1ZOV1Z3PT06M2I4ODk0ZGQ=


def ensure_config(*configs: RunnableConfig | None) -> RunnableConfig:
    """Return a config with all keys, merging any provided configs.

    Args:
        *configs: Configs to merge before ensuring defaults.

    Returns:
        RunnableConfig: The merged and ensured config.
    """
    empty = _Config(
        tags=[],
        metadata=ChainMap(),
        callbacks=None,
        recursion_limit=DEFAULT_RECURSION_LIMIT,
        configurable={},
    )
    if var_child_runnable_config is not None and (
        var_config := var_child_runnable_config.get()
    ):
        empty.update(
            {
                k: v.copy() if k in COPIABLE_KEYS else v  # type: ignore[attr-defined]
                for k, v in var_config.items()
                if _is_not_empty(v)
            },
        )
    for config in configs:
        if config is None:
            continue
        for k, v in config.items():
            if _is_not_empty(v) and k in CONFIG_KEYS:
                if k == CONF:
                    empty[k] = v.copy()  # type: ignore
                else:
                    empty[k] = v  # type: ignore[literal-required]
        for k, v in config.items():
            if _is_not_empty(v) and k not in CONFIG_KEYS:
                empty[CONF][k] = v
    for key, value in empty[CONF].items():
        if (
            not key.startswith("__")
            and isinstance(value, str | int | float | bool)
            and key not in empty["metadata"]
        ):
            empty["metadata"][key] = value
    return empty
# pylint: disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2U1ZOV1Z3PT06M2I4ODk0ZGQ=


async def run_in_executor(
    executor_or_config: Executor | RunnableConfig | None,
    func: typing.Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """Run a function in an executor.

    Args:
        executor_or_config: The executor or config to run in.
        func (Callable[P, Output]): The function.
        *args (Any): The positional arguments to the function.
        **kwargs (Any): The keyword arguments to the function.

    Returns:
        Output: The output of the function.

    Raises:
        RuntimeError: If the function raises a StopIteration.
    """

    def wrapper() -> T:
        try:
            return func(*args, **kwargs)
        except StopIteration as exc:
            # StopIteration can't be set on an asyncio.Future
            # it raises a TypeError and leaves the Future pending forever
            # so we need to convert it to a RuntimeError
            raise RuntimeError from exc

    if executor_or_config is None or isinstance(executor_or_config, dict):
        # Use default executor with context copied from current context
        return await asyncio.get_running_loop().run_in_executor(
            None,
            functools.partial(copy_context().run, wrapper),
        )

    return await asyncio.get_running_loop().run_in_executor(executor_or_config, wrapper)
