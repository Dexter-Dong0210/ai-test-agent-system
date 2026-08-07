"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Any
# noqa  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2U3pOcWF3PT06YWU3OTNiZjQ=

from starlette.responses import Response, StreamingResponse
from starlette.types import Send

from langgraph_api.serde import Fragment, json_dumpb

"""
Patch Response.render and StreamingResponse.stream_response
to recognize bytearrays and memoryviews as bytes-like objects.
"""


def Response_render(self, content: Any) -> bytes:
    if content is None:
        return b""
    if isinstance(content, (bytes, bytearray, memoryview)):
        return content
    return content.encode(self.charset)  # type: ignore


async def StreamingResponse_stream_response(self, send: Send) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.raw_headers,
        }
    )
    async for chunk in self.body_iterator:
        if chunk is None:
            continue
        if isinstance(chunk, Fragment):
            chunk = chunk.buf
        if isinstance(chunk, dict):
            chunk = json_dumpb(chunk)
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            chunk = chunk.encode(self.charset)
        await send({"type": "http.response.body", "body": chunk, "more_body": True})

    await send({"type": "http.response.body", "body": b"", "more_body": False})
# fmt: off  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2U3pOcWF3PT06YWU3OTNiZjQ=


# patch StreamingResponse.stream_response

StreamingResponse.stream_response = StreamingResponse_stream_response  # type: ignore[invalid-assignment]

# patch Response.render
# pragma: no cover  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2U3pOcWF3PT06YWU3OTNiZjQ=

Response.render = Response_render  # type: ignore[invalid-assignment]
