"""Sweeping logic for cleaning up expired threads and checkpoints."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import asyncio
from typing import cast
# pragma: no cover  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVsNmFnPT06OTBlMTkwYTI=

import structlog

from langgraph_api.config import THREAD_TTL
from langgraph_runtime.database import connect

logger = structlog.stdlib.get_logger(__name__)

# type: ignore  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVsNmFnPT06OTBlMTkwYTI=

async def thread_ttl_sweep_loop():
    """Periodically delete threads based on TTL configuration.

    Currently implements the 'delete' strategy, which deletes entire threads
    that have been inactive for longer than their configured TTL period.
    """
    # Use the same interval as store TTL sweep
    thread_ttl_config = THREAD_TTL or {}
    strategy = thread_ttl_config.get("strategy", "delete")
    if strategy != "delete":
        raise NotImplementedError(
            f"Unrecognized thread deletion strategy: {strategy}. Expected 'delete'."
        )
    sweep_interval_minutes = cast(
        "int", thread_ttl_config.get("sweep_interval_minutes", 5)
    )
    await logger.ainfo(
        f"Starting thread TTL sweeper with interval {sweep_interval_minutes} minutes",
        strategy=strategy,
        interval_minutes=sweep_interval_minutes,
    )
    loop = asyncio.get_running_loop()

    from langgraph_runtime.ops import Threads

    while True:
        await asyncio.sleep(sweep_interval_minutes * 60)
        try:
            async with connect() as conn:
                sweep_start = loop.time()
                threads_processed, threads_deleted = await Threads.sweep_ttl(conn)
                if threads_processed > 0:
                    await logger.ainfo(
                        f"Thread TTL sweep completed. Processed {threads_processed}",
                        threads_processed=threads_processed,
                        threads_deleted=threads_deleted,
                        duration=loop.time() - sweep_start,
                    )
        except Exception as exc:
            logger.exception("Thread TTL sweep iteration failed", exc_info=exc)
# pragma: no cover  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVsNmFnPT06OTBlMTkwYTI=
