from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_FILE = PROJECT_ROOT / "supabase" / "migrations" / "0001_init.sql"


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def split_statements(sql: str) -> list[str]:
    statements: list[str] = []
    for chunk in sql.split(";\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        statements.append(chunk if chunk.endswith(";") else chunk + ";")
    return statements


def run() -> int:
    load_env()
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print("SUPABASE_DB_URL is not set", file=sys.stderr)
        return 1
    sql = MIGRATION_FILE.read_text(encoding="utf-8")
    statements = split_statements(sql)
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                for idx, statement in enumerate(statements, start=1):
                    cur.execute(statement)
                    preview = statement.splitlines()[0]
                    print(f"OK [{idx:02d}/{len(statements):02d}] {preview[:80]}")
    except Exception as exc:
        print(f"MIGRATION FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())