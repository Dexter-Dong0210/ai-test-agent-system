"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langgraph_api import config
from typing_extensions import TypedDict

from langgraph_runtime_postgres import queue


class WorkerMetrics(TypedDict):
    max: int
    active: int
    available: int
# noqa  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WVhGeFp3PT06ZjhkNmI3YTI=

# noqa  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WVhGeFp3PT06ZjhkNmI3YTI=

class Metrics(TypedDict):
    workers: WorkerMetrics


def get_metrics() -> Metrics:
    workers_max = config.N_JOBS_PER_WORKER
    workers_active = queue.get_num_workers()
    return Metrics(
        workers=WorkerMetrics(
            max=workers_max,
            active=workers_active,
            available=workers_max - workers_active,
        )
    )
