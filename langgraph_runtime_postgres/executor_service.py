"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import contextlib
from typing import TypeVar
# type: ignore  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2WmxObGJ3PT06Y2IwYWJiNzU=

import grpc
import grpc.aio
import structlog
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph_api import config as api_config
from langgraph_api import store as api_store
from langgraph_api.logging import LOG_LEVEL
from langgraph_executor import executor_base
from langgraph_executor import serde as executor_serde
from langgraph_executor.proto.executor_api_pb2_grpc import (
    add_LangGraphExecutorServicer_to_server,
)

logger = structlog.stdlib.get_logger(__name__)

T = TypeVar("T")
NS_SEP = "|"
DEBUG = LOG_LEVEL == "DEBUG"


async def start_executor(port: int = 50052):
    from langgraph_api.graph import GRAPHS
    from langgraph_api.serde import Serializer

    executor_serde.set_serializer(Serializer(pickle_fallback=False))
# fmt: off  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2WmxObGJ3PT06Y2IwYWJiNzU=

    logger.info(f"Initializing python executor on port {port}.")

    if api_config.LANGGRAPH_AES_KEY:
        await logger.ainfo("Setting executor's serializer to AES key")
        executor_serde.set_serializer(
            # TODO: do we actually want to **encrypt** here? Or maybe only in apply writes, etc.
            EncryptedSerializer.from_pycryptodome_aes(
                executor_serde.get_serializer(), key=api_config.LANGGRAPH_AES_KEY
            )
        )

    server = grpc.aio.server(
        # Be permissive: allow client pings without active RPCs and accept intervals
        # as low as 50s. Our clients still default to ~5m, but this avoids penalizing
        # other, more frequent clients.
        options=[
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.min_recv_ping_interval_without_data_ms", 50000),  # 50s
            ("grpc.http2.max_ping_strikes", 2),
            # Set max message size from config
            (
                "grpc.max_receive_message_length",
                api_config.GRPC_SERVER_MAX_RECV_MSG_BYTES,
            ),
            ("grpc.max_send_message_length", api_config.GRPC_SERVER_MAX_SEND_MSG_BYTES),
        ],
    )
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2WmxObGJ3PT06Y2IwYWJiNzU=

    add_LangGraphExecutorServicer_to_server(
        executor_base.LangGraphExecutorServicer(
            sorted(GRAPHS),
            get_graph=get_graph_wrapped,
            get_store=api_store.get_store,
        ),
        server,
    )
    # Bind and start serving
    resolved_port = server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info(f"LangGraph Executor gRPC server started on port {resolved_port}")
    await server.wait_for_termination()


@contextlib.asynccontextmanager
async def get_graph_wrapped(
    graph_id: str,
    config: RunnableConfig,
):
    from langgraph_api.graph import get_graph as get_graph_base
# noqa  My80OmFIVnBZMlhva2FQbHNJL21tS1U2WmxObGJ3PT06Y2IwYWJiNzU=

    async with get_graph_base(
        graph_id,
        config,
        store=await api_store.get_store(),
    ) as graph:
        yield graph
