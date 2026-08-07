"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
from random import random

import structlog
# type: ignore  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2Vm1aM1J3PT06ZTI0OGNjZGY=

from langgraph_api.models.run import create_valid_run
from langgraph_api.utils import next_cron_date
from langgraph_api.utils.config import run_in_executor
from langgraph_api.worker import set_auth_ctx_for_run
from langgraph_runtime.database import connect
from langgraph_runtime.ops import Crons
from langgraph_runtime.retry import retry_db
# fmt: off  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2Vm1aM1J3PT06ZTI0OGNjZGY=

logger = structlog.stdlib.get_logger(__name__)

SLEEP_TIME = 5


@retry_db
async def cron_scheduler():
    logger.info("Starting cron scheduler")
    while True:
        try:
            async with connect() as conn:
                async for cron in Crons.next(conn):
                    on_run_completed = cron.get("on_run_completed")

                    run_payload = cron["payload"]
# type: ignore  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2Vm1aM1J3PT06ZTI0OGNjZGY=

                    if on_run_completed == "keep":
                        run_payload.setdefault("on_completion", "keep")  # type: ignore[union-attr]
# fmt: off  My80OmFIVnBZMlhva2FQbHNJL21tS1U2Vm1aM1J3PT06ZTI0OGNjZGY=

                    async with set_auth_ctx_for_run(
                        run_payload, user_id=cron["user_id"]
                    ):
                        logger.debug(f"Scheduling cron run {cron}")
                        try:
                            run = await create_valid_run(
                                conn,
                                thread_id=(
                                    str(cron.get("thread_id"))
                                    if cron.get("thread_id")
                                    else None
                                ),
                                payload=run_payload,
                                headers={},
                            )
                            if not run:
                                logger.error(
                                    "Run not created for cron_id={} payload".format(
                                        cron["cron_id"],
                                    )
                                )
                        except Exception:
                            logger.exception(
                                "Error scheduling cron run cron_id={}".format(
                                    cron["cron_id"]
                                )
                            )
                        next_run_date = await run_in_executor(
                            None, next_cron_date, cron["schedule"], cron["now"]
                        )
                        await Crons.set_next_run_date(
                            conn, cron["cron_id"], next_run_date
                        )

            await asyncio.sleep(SLEEP_TIME)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Error in cron_scheduler")
            await asyncio.sleep(SLEEP_TIME + random())
