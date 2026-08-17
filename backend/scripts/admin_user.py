from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ADMIN_EMAIL = "admin@ffmitra.local"
ADMIN_PASSWORD = "Analyst@2026"


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def create_analyst_user() -> int:
    supabase_url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    secret = os.environ.get("SUPABASE_SECRET_KEY")
    if not supabase_url or not secret:
        print("SUPABASE_URL and SUPABASE_SECRET_KEY must be set", file=sys.stderr)
        return 1
    url = f"{supabase_url}/auth/v1/admin/users"
    headers = {"apikey": secret, "Authorization": f"Bearer {secret}"}
    body = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "email_confirm": True}
    resp = httpx.post(url, headers=headers, json=body, timeout=30.0)
    if resp.status_code in (200, 201):
        print(f"Created analyst user {ADMIN_EMAIL} (HTTP {resp.status_code})")
        return 0
    if resp.status_code in (400, 422):
        print(f"already exists (HTTP {resp.status_code})")
        return 0
    print(f"Failed to create user: HTTP {resp.status_code} {resp.text}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    load_env()
    sys.exit(create_analyst_user())