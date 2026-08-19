"""In-memory fixed-window rate limiting for public endpoints.

Single-instance friendly; for multi-instance deployments swap the store
for Redis (same call shape). The table is pruned opportunistically.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class _FixedWindow:
    def __init__(self, max_calls: int, window: float) -> None:
        self.max_calls = max_calls
        self.window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._last_prune = 0.0

    def _prune(self, now: float) -> None:
        if now - self._last_prune < 60.0:
            return
        self._last_prune = now
        stale = [k for k, q in self._hits.items() if not q or now - q[-1] > self.window]
        for k in stale:
            self._hits.pop(k, None)

    def check(self, key: str) -> bool:
        now = time.monotonic()
        self._prune(now)
        q = self._hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max_calls:
            return False
        q.append(now)
        return True


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(max_calls: int, window: float = 60.0, scope: str = "default"):
    """FastAPI dependency: per-IP fixed window; raises HTTP 429 when exceeded."""
    bucket = _FixedWindow(max_calls, window)

    async def dependency(request: Request) -> str:
        key = f"{scope}:{_client_ip(request)}"
        allowed = bucket.check(key)
        if not allowed:
            raise HTTPException(
                429,
                f"rate limit exceeded: max {max_calls} requests per {int(window)}s",
            )
        return _client_ip(request)

    return dependency