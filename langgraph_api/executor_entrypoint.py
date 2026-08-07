"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import argparse
import asyncio
import json
import logging.config
import pathlib
# fmt: off  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2YW5wWVp3PT06OGQwMmQ3NDg=

from langgraph_api.queue_entrypoint import main as queue_main


async def main(grpc_port: int = 50051):
    with open(pathlib.Path(__file__).parent.parent / "logging.json") as file:
        loaded_config = json.load(file)
        logging.config.dictConfig(loaded_config)
    try:
        import uvloop  # type: ignore[unresolved-import]

        uvloop.install()
    except ImportError:
        pass
    from langgraph_api import config

    config.IS_EXECUTOR_ENTRYPOINT = True
    await queue_main(grpc_port=grpc_port, entrypoint_name="python-executor")

# fmt: off  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2YW5wWVp3PT06OGQwMmQ3NDg=

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--grpc-port", type=int, default=50051)
    args = parser.parse_args()
    asyncio.run(main(grpc_port=args.grpc_port))
