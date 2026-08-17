"""Supabase data access layer via the PostgREST REST API (service key).

No direct DB credentials are needed: every operation goes through the
Supabase REST gateway, which also applies RLS for public (anon) traffic.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx

from .config import get_settings

_OP_MAP = {
    "eq": "eq",
    "neq": "neq",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
    "like": "like",
    "ilike": "ilike",
    "in": "in",
    "is": "is",
}


class DbError(RuntimeError):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(f"Supabase API error {status}: {detail}")
        self.status = status
        self.detail = detail


class SupabaseDB:
    """Thin async PostgREST client."""

    def __init__(self, url: str, service_key: str) -> None:
        self.base = url.rstrip("/") + "/rest/v1"
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    def _filters(filters: Optional[dict]) -> dict:
        if not filters:
            return {}
        params: dict[str, str] = {}

        def quote(v: Any) -> str:
            s = str(v)
            if s == "":
                return '""'
            if any(ch in s for ch in " ,"):
                return f'"{s}"'
            return s

        for key, value in filters.items():
            if "__" in key:
                field, op = key.rsplit("__", 1)
                if op not in _OP_MAP:
                    field, op = key, "eq"
            else:
                field, op = key, "eq"
            if op == "in" and isinstance(value, (list, tuple)):
                params[field] = "in.(" + ",".join(quote(v) for v in value) + ")"
            elif op == "is":
                params[field] = f"is.{value}"
            elif op in ("like", "ilike"):
                params[field] = f"{op}.{quote('*' + str(value) + '*')}"
            else:
                params[field] = f"{op}.{quote(value)}"
        return params

    async def _request(
        self,
        method: str,
        table: str,
        params: Optional[dict] = None,
        json_body: Any = None,
        prefer: str = "return=representation",
        extra_headers: Optional[dict] = None,
    ) -> Any:
        headers = dict(self.headers)
        headers["Prefer"] = prefer
        if extra_headers:
            headers.update(extra_headers)
        try:
            resp = await self.client.request(
                method, f"{self.base}/{table}", params=params, json=json_body, headers=headers
            )
        except httpx.HTTPError as exc:
            raise DbError(0, f"network error: {exc}") from exc
        if resp.status_code >= 400:
            raise DbError(resp.status_code, resp.text[:500])
        if resp.status_code == 204 or not resp.content:
            return []
        return resp.json()

    async def select(
        self,
        table: str,
        filters: Optional[dict] = None,
        columns: str = "*",
        order: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        params = self._filters(filters)
        if order:
            params["order"] = order
        if limit is not None:
            params["limit"] = str(limit)
        if offset:
            params["offset"] = str(offset)
        return await self._request("GET", table, params=params)

    async def get_one(self, table: str, filters: dict, columns: str = "*") -> Optional[dict]:
        rows = await self.select(table, filters, columns=columns, limit=1)
        return rows[0] if rows else None

    async def insert(
        self,
        table: str,
        rows: list[dict],
        on_conflict: Optional[str] = None,
        upsert: bool = False,
    ) -> list[dict]:
        if not rows:
            return []
        params: dict[str, str] = {}
        if on_conflict:
            params["on_conflict"] = on_conflict
        prefer = "return=representation"
        if upsert or on_conflict:
            prefer = "resolution=merge-duplicates,return=representation"
        return await self._request("POST", table, params=params, json_body=rows, prefer=prefer)

    async def update(
        self, table: str, filters: dict, values: dict
    ) -> list[dict]:
        return await self._request(
            "PATCH", table, params=self._filters(filters), json_body=values
        )

    async def delete(self, table: str, filters: dict) -> list[dict]:
        return await self._request("DELETE", table, params=self._filters(filters))

    async def count(self, table: str, filters: Optional[dict] = None) -> int:
        params = self._filters(filters)
        params["select"] = "count"
        headers = dict(self.headers)
        headers["Prefer"] = "count=exact"
        try:
            resp = await self.client.request(
                "HEAD", f"{self.base}/{table}", params=params, headers=headers
            )
            return int(resp.headers.get("content-range", "0/0").split("/")[-1])
        except (httpx.HTTPError, ValueError):
            return 0


_db: Optional[SupabaseDB] = None


def get_db() -> SupabaseDB:
    global _db
    if _db is None:
        s = get_settings()
        _db = SupabaseDB(s.supabase_url, s.supabase_secret_key)
    return _db


async def db_health() -> dict:
    db = get_db()
    try:
        txn_count = await db.count("transactions")
        flagged = await db.count("flagged_accounts", {"active": "true"})
        return {"ok": True, "transactions": txn_count, "flagged": flagged}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)[:300]}


async def close_db() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


def ensure_no_pending() -> None:
    pass