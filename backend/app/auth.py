"""Supabase JWT verification via token introspection (no JWT secret needed)."""

from __future__ import annotations

import time
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

_bearer = HTTPBearer(auto_error=False)
_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 120.0


async def introspect_user(token: str) -> Optional[dict]:
    """Validate a Supabase access token and return the user object."""
    now = time.monotonic()
    cached = _cache.get(token)
    if cached and now - cached[0] < _CACHE_TTL:
        return cached[1]
    settings = get_settings()
    if not settings.supabase_url:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_publishable_key,
                },
            )
        if resp.status_code != 200:
            return None
        user = resp.json()
        _cache[token] = (now, user)
        return user
    except httpx.HTTPError:
        return None


def _user_role(user: dict) -> str:
    app_meta = user.get("app_metadata") or {}
    if user.get("email") and user["email"].endswith("@ffmitra.local"):
        return "admin"
    role = app_meta.get("role") or user.get("user_metadata", {}).get("role") or "analyst"
    return str(role)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing credentials")
    user = await introspect_user(credentials.credentials)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or expired token")
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": _user_role(user),
        "token": credentials.credentials,
    }


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin role required")
    return user


async def optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Optional[dict]:
    if credentials is None:
        return None
    user = await introspect_user(credentials.credentials)
    if user is None:
        return None
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": _user_role(user),
        "token": credentials.credentials,
    }