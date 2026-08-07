"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

T = TypeVar("T")

# pragma: no cover  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2WW1oM1F3PT06NjFkZjBlMzQ=

class LRUCache(Generic[T]):
    """LRU cache with TTL and proactive refresh support."""

    def __init__(
        self,
        max_size: int = 1000,
        ttl: float = 60,
        refresh_window: float = 30,
        refresh_callback: Callable[[str], Awaitable[T | None]] | None = None,
    ):
        self._cache: OrderedDict[str, tuple[T, float, bool]] = OrderedDict()
        self._max_size = max_size if max_size > 0 else 1000
        self._ttl = ttl
        self._refresh_window = refresh_window if refresh_window > 0 else 30
        self._refresh_callback = refresh_callback

    def _get_time(self) -> float:
        """Get current time, using loop.time() if available for better performance."""
        try:
            return asyncio.get_event_loop().time()
        except RuntimeError:
            return time.monotonic()
# noqa  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2WW1oM1F3PT06NjFkZjBlMzQ=

    async def get(self, key: str) -> T | None:
        """Get item from cache, attempting refresh if within refresh window."""
        if key not in self._cache:
            return None

        value, timestamp, is_refreshing = self._cache[key]
        current_time = self._get_time()
        time_until_expiry = self._ttl - (current_time - timestamp)

        # Check if expired
        if time_until_expiry <= 0:
            del self._cache[key]
            return None
# pylint: disable  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2WW1oM1F3PT06NjFkZjBlMzQ=

        # Check if we should attempt refresh (within refresh window and not already refreshing)
        if (
            time_until_expiry <= self._refresh_window
            and not is_refreshing
            and self._refresh_callback
        ):
            # Mark as refreshing to prevent multiple simultaneous refresh attempts
            self._cache[key] = (value, timestamp, True)

            try:
                # Attempt refresh
                refreshed_value = await self._refresh_callback(key)
                if refreshed_value is not None:
                    # Refresh successful, update cache with new value
                    self._cache[key] = (refreshed_value, current_time, False)
                    # Move to end (most recently used)
                    self._cache.move_to_end(key)
                    return refreshed_value
                else:
                    # Refresh failed, fallback to cached value
                    self._cache[key] = (value, timestamp, False)
            except Exception:
                # Refresh failed with exception, fallback to cached value
                self._cache[key] = (value, timestamp, False)

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: T) -> None:
        """Set item in cache, evicting old entries if needed."""
        # Remove if already exists (to update timestamp)
        if key in self._cache:
            del self._cache[key]

        # Evict oldest entries if needed
        while len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove oldest (FIFO)

        # Add new entry (not refreshing initially)
        self._cache[key] = (value, self._get_time(), False)
# pragma: no cover  My80OmFIVnBZMlhva2FQbHNJL21tS1U2WW1oM1F3PT06NjFkZjBlMzQ=

    def size(self) -> int:
        """Return current cache size."""
        return len(self._cache)

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
