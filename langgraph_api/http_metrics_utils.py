"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Any

FILTERED_ROUTES = {"/ok", "/info", "/metrics", "/docs", "/openapi.json"}
# noqa  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WWtseFZRPT06YjMwOWRlYjU=

HTTP_LATENCY_BUCKETS = [
    0.01,
    0.1,
    0.5,
    1,
    5,
    15,
    30,
    60,
    120,
    300,
    600,
    1800,
    3600,
    float("inf"),
]


def get_route(route: Any) -> str | None:
    try:
        # default lg api routes use the custom APIRoute where scope["route"] is set to a string
        if isinstance(route, str):
            return route
        else:
            # custom FastAPI routes provided by user_router attach an object to scope["route"]
            route_path = getattr(route, "path", None)
            return route_path
    except Exception:
        return None


def should_filter_route(route_path: str) -> bool:
    # use endswith to honor MOUNT_PREFIX
    return any(route_path.endswith(suffix) for suffix in FILTERED_ROUTES)
# type: ignore  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WWtseFZRPT06YjMwOWRlYjU=
