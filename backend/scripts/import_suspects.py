from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FLAGGED_TABLE = "flagged_accounts"


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def rest_url() -> str:
    return f"{os.environ['SUPABASE_URL'].rstrip('/')}/rest/v1"


def headers() -> dict[str, str]:
    secret = os.environ["SUPABASE_SECRET_KEY"]
    return {
        "apikey": secret,
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal,resolution=merge-duplicates",
    }


def read_suspects(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            data = data.get("suspects", [])
        return [dict(row) for row in data if isinstance(row, dict)]
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append(dict(row))
    return rows


def import_suspects(rows: list[dict], source: str, severity: str, client: httpx.Client) -> int:
    payload: list[dict] = []
    for row in rows:
        account_ref = (row.get("account_ref") or "").strip()
        if not account_ref:
            continue
        payload.append({
            "account_ref": account_ref,
            "reason": (row.get("reason") or "").strip(),
            "source": source,
            "severity": severity,
        })
    if not payload:
        return 0
    resp = client.post(f"{rest_url()}/{FLAGGED_TABLE}", params={"on_conflict": "account_ref"}, headers=headers(), json=payload)
    resp.raise_for_status()
    return len(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import suspected fraud accounts into flagged_accounts")
    parser.add_argument("path", type=Path, help="CSV (account_ref,reason) or JSON list of suspect objects")
    parser.add_argument("--source", default="SUSPECT_IMPORT", help="Source label for imported suspects")
    parser.add_argument("--severity", default="HIGH", help="Severity for imported suspects")
    args = parser.parse_args(argv)
    load_env()
    if not (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SECRET_KEY")):
        print("SUPABASE_URL and SUPABASE_SECRET_KEY must be set", file=sys.stderr)
        return 1
    rows = read_suspects(args.path)
    try:
        with httpx.Client(timeout=60.0) as client:
            count = import_suspects(rows, args.source, args.severity, client)
    except httpx.HTTPError as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    print(f"Imported {count} suspect(s) into flagged_accounts")
    return 0


if __name__ == "__main__":
    sys.exit(main())