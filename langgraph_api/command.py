"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import cast
# pragma: no cover  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VGt0WGVnPT06ZjFmODYzYzg=

from langgraph.types import Command, Send

from langgraph_api.schema import RunCommand

# pylint: disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VGt0WGVnPT06ZjFmODYzYzg=

def map_cmd(cmd: RunCommand) -> Command:
    goto = cmd.get("goto")
    if goto is not None and not isinstance(goto, list):
        goto = [cmd.get("goto")]

    update = cmd.get("update")
    if isinstance(update, tuple | list) and all(
        isinstance(t, tuple | list) and len(t) == 2 and isinstance(t[0], str)
        for t in cast("list", update)
    ):
        update = [tuple(t) for t in cast("list", update)]

    return Command(
        update=update,
        goto=(
            [
                it if isinstance(it, str) else Send(it["node"], it["input"])  # type: ignore[non-subscriptable]
                for it in goto
            ]
            if goto
            else None
        ),
        resume=cmd.get("resume"),
    )
