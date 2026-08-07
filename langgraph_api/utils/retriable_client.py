"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
# noqa  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2ZVhOM1NnPT06MDIxMTE0ZTk=

import httpx
import structlog

logger = structlog.stdlib.get_logger(__name__)
# noqa  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2ZVhOM1NnPT06MDIxMTE0ZTk=


async def _make_http_request_with_retries(
    url: str,
    headers: dict,
    method: str = "GET",
    json_data: dict | None = None,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> httpx.Response | None:
    """
    Make an HTTP request with exponential backoff retries.

    Args:
        url: The URL to request
        headers: Headers to include in the request
        method: HTTP method ("GET" or "POST")
        json_data: JSON data for POST requests
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff

    Returns:
        httpx.Response: The successful response

    Raises:
        httpx.HTTPStatusError: If the request fails after all retries
        httpx.RequestError: If the request fails after all retries
    """
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(
                    method, url, headers=headers, json=json_data
                )
                response.raise_for_status()
                return response
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2ZVhOM1NnPT06MDIxMTE0ZTk=

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RequestError,
            httpx.HTTPStatusError,
        ) as e:
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                # Don't retry on 4xx errors, but do on 5xxs
                raise e
# pylint: disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2ZVhOM1NnPT06MDIxMTE0ZTk=

            # Back off and retry if we haven't reached the max retries
            if attempt < max_retries:
                delay = base_delay * (2**attempt)  # Exponential backoff
                logger.warning(
                    "HTTP %s request attempt %d to %s failed: %s. Retrying in %.1f seconds...",
                    method,
                    attempt + 1,
                    url,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.exception(
                    "HTTP %s request to %s failed after %d attempts. Last error: %s",
                    method,
                    url,
                    max_retries + 1,
                    e,
                )
                raise e
