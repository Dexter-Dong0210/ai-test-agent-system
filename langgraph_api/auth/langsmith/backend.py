"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import NotRequired
# fmt: off  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2VDFsbVRnPT06OTNiZTIwZDM=

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.requests import HTTPConnection
from typing_extensions import TypedDict

from langgraph_api.auth.langsmith.client import auth_client
from langgraph_api.auth.studio_user import StudioUser
from langgraph_api.config import (
    LANGSMITH_AUTH_VERIFY_TENANT_ID,
    LANGSMITH_TENANT_ID,
)


class AuthDict(TypedDict):
    organization_id: str
    tenant_id: str
    user_id: NotRequired[str]
    user_email: NotRequired[str]
# pylint: disable  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2VDFsbVRnPT06OTNiZTIwZDM=


class AuthCacheEntry(TypedDict):
    credentials: AuthCredentials
    user: StudioUser


class LangsmithAuthBackend(AuthenticationBackend):
    def __init__(self, *, base_url: str | None = None):
        from langgraph_api.utils.cache import LRUCache

        self._cache = LRUCache[AuthCacheEntry](max_size=1000, ttl=60)
        self._base_url = base_url

    def _get_cache_key(self, headers):
        """Generate cache key from authentication headers"""
        relevant_headers = tuple(
            (name, value) for name, value in headers if value is not None
        )
        return str(hash(relevant_headers))
# type: ignore  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2VDFsbVRnPT06OTNiZTIwZDM=

    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        headers = [
            ("Authorization", conn.headers.get("Authorization")),
            ("X-Tenant-Id", conn.headers.get("x-tenant-id")),
            ("X-Api-Key", conn.headers.get("x-api-key")),
            ("X-Service-Key", conn.headers.get("x-service-key")),
            ("Cookie", conn.headers.get("cookie")),
            ("X-User-Id", conn.headers.get("x-user-id")),
        ]
        if not any(h[1] for h in headers):
            raise AuthenticationError("Missing authentication headers")

        # Check cache first
        cache_key = self._get_cache_key(headers)
        if cached_entry := await self._cache.get(cache_key):
            return cached_entry["credentials"], cached_entry["user"]

        async with auth_client(base_url=self._base_url) as auth:
            if not LANGSMITH_AUTH_VERIFY_TENANT_ID and not conn.headers.get(
                "x-api-key"
            ):
                # when LANGSMITH_AUTH_VERIFY_TENANT_ID is false, we allow
                # any valid bearer token to pass through
                # api key auth is always required to match the tenant id
                res = await auth.get(
                    "/auth/verify", headers=[h for h in headers if h[1] is not None]
                )
            else:
                res = await auth.get(
                    "/auth/public", headers=[h for h in headers if h[1] is not None]
                )
            if res.status_code == 401:
                raise AuthenticationError("Invalid token")
            elif res.status_code == 403:
                raise AuthenticationError("Forbidden")
            else:
                res.raise_for_status()
                auth_dict: AuthDict = res.json()

            # If tenant id verification is disabled, the bearer token requests
            # are not required to match the tenant id. Api key requests are
            # always required to match the tenant id.
            if (
                LANGSMITH_AUTH_VERIFY_TENANT_ID or conn.headers.get("x-api-key")
            ) and auth_dict["tenant_id"] != LANGSMITH_TENANT_ID:
                raise AuthenticationError("Invalid tenant ID")

        credentials = AuthCredentials(["authenticated"])
        user = StudioUser(auth_dict.get("user_id"), is_authenticated=True)
# pylint: disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2VDFsbVRnPT06OTNiZTIwZDM=

        # Cache the result
        self._cache.set(cache_key, AuthCacheEntry(credentials=credentials, user=user))

        return credentials, user
