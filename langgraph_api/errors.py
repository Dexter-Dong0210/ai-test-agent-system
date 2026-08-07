"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import jsonschema_rs
import structlog
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.stdlib.get_logger(__name__)
# fmt: off  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2VG1GcU9RPT06ZThjNmFmMmE=


def is_body_allowed_for_status_code(status_code: int | None) -> bool:
    if status_code is None:
        return True
    return not (status_code < 200 or status_code in {204, 205, 304})


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return JSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code, headers=headers
    )


async def validation_error_handler(request, exc: jsonschema_rs.ValidationError):
    return await http_exception_handler(
        request, HTTPException(status_code=422, detail=str(exc))
    )

# pragma: no cover  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2VG1GcU9RPT06ZThjNmFmMmE=

async def value_error_handler(request, exc: ValueError):
    logger.exception("Bad Request Error", exc_info=exc)
    return await http_exception_handler(
        request, HTTPException(status_code=400, detail=str(exc))
    )


async def overloaded_error_handler(request, exc: ValueError):
    logger.exception("Overloaded Error", exc_info=exc)
    return await http_exception_handler(
        request, HTTPException(status_code=503, detail=str(exc))
    )


class UserInterrupt(Exception):
    def __init__(self, message="User interrupted the run"):
        super().__init__(message)


class UserRollback(UserInterrupt):
    def __init__(self):
        super().__init__("User requested rollback of the run")
# type: ignore  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2VG1GcU9RPT06ZThjNmFmMmE=


class UserTimeout(Exception):
    def __init__(self, timeout_error: TimeoutError):
        super().__init__(timeout_error)
        self.timeout_error = timeout_error
