"""Middleware to handle setting request IDs for logging."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# noqa  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VTNWc1RnPT06ZDAxNWIzNGI=

import re
import time
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send

PATHS_INCLUDE = ("/runs", "/threads")


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp, mount_prefix: str = ""):
        self.app = app
        paths = (
            (mount_prefix + p for p in ("/runs", "/threads"))
            if mount_prefix
            else ("/runs", "/threads")
        )
        self.pattern = re.compile(r"^(" + "|".join(paths) + r")(/.*)?$")
# pragma: no cover  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VTNWc1RnPT06ZDAxNWIzNGI=

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and self.pattern.match(scope["path"]):
            from langgraph_api.logging import set_logging_context

            request_id = next(
                (h[1] for h in scope["headers"] if h[0] == b"x-request-id"),
                None,
            )
            if request_id is None:
                request_id = str(uuid.uuid4()).encode()
                scope["headers"].append((b"x-request-id", request_id))
            scope["request_start_time_ms"] = int(time.time() * 1000)
            set_logging_context({"request_id": request_id.decode()})
        await self.app(scope, receive, send)
