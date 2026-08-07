"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
# pragma: no cover  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2VWs1dU9BPT06NjdkODEzOWI=

import structlog

from langgraph_api.config import HTTP_CONFIG
from langgraph_api.http import get_http_client, get_loopback_client, http_request

if TYPE_CHECKING:
    from langgraph_api.worker import WorkerResult
# fmt: off  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2VWs1dU9BPT06NjdkODEzOWI=

logger = structlog.stdlib.get_logger(__name__)


async def call_webhook(result: "WorkerResult") -> None:
    if HTTP_CONFIG and HTTP_CONFIG.get("disable_webhooks"):
        logger.info(
            "Webhooks disabled, skipping webhook call", webhook=result["webhook"]
        )
        return
# pragma: no cover  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2VWs1dU9BPT06NjdkODEzOWI=

    checkpoint = result["checkpoint"]
    payload = {
        **result["run"],
        "status": result["status"],
        "run_started_at": result["run_started_at"],
        "run_ended_at": result["run_ended_at"],
        "webhook_sent_at": datetime.now(UTC).isoformat(),
        "values": checkpoint["values"] if checkpoint else None,
    }
    if exception := result["exception"]:
        payload["error"] = str(exception)
    webhook = result.get("webhook")
    if webhook:
        try:
            if webhook.startswith("/"):
                # Call into this own app
                webhook_client = get_loopback_client()
            else:
                webhook_client = get_http_client()
            await http_request("POST", webhook, json=payload, client=webhook_client)
            await logger.ainfo(
                "Background worker called webhook",
                webhook=result["webhook"],
                run_id=result["run"]["run_id"],
            )
        except Exception as exc:
            logger.exception(
                f"Background worker failed to call webhook {result['webhook']}",
                exc_info=exc,
                webhook=result["webhook"],
            )
