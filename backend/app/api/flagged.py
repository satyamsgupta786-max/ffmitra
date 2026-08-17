"""Flagged accounts (watchlist/blacklist) + suspect import endpoints."""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..auth import get_current_user
from ..db import get_db
from ..schemas import FlagIn, UnflagIn
from ..services.enforcement import flag_account, unflag_account

router = APIRouter(prefix="/api/flagged", tags=["flagged"])


@router.get("")
async def list_flagged(
    active: Optional[str] = "true", _user: dict = Depends(get_current_user)
) -> dict:
    db = get_db()
    filters: dict = {}
    if active in ("true", "false"):
        filters["active"] = active
    rows = await db.select("flagged_accounts", filters, order="created_at.desc", limit=500)
    return {"flagged": rows, "count": len(rows)}


@router.post("")
async def flag(flag: FlagIn, user: dict = Depends(get_current_user)) -> dict:
    row = await flag_account(
        flag.account_ref,
        reason=flag.reason,
        severity=flag.severity,
        source=flag.source,
        flagged_by=user.get("email") or "system",
    )
    return {"flagged": row}


@router.post("/unflag")
async def unflag(body: UnflagIn, _user: dict = Depends(get_current_user)) -> dict:
    await unflag_account(body.account_ref)
    return {"unflagged": body.account_ref}


@router.post("/import")
async def import_suspects(
    file: UploadFile = File(...),
    source: str = "SUSPECT_IMPORT",
    severity: str = "HIGH",
    _user: dict = Depends(get_current_user),
) -> dict:
    content = await file.read()
    text = content.decode("utf-8-sig", errors="replace")
    entries: list[dict] = []
    if file.filename and file.filename.endswith(".json"):
        data = json.loads(text)
        for item in data:
            if isinstance(item, dict) and item.get("account_ref"):
                entries.append(item)
    else:
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            acc = (row.get("account_ref") or row.get("account") or "").strip()
            if acc:
                entries.append({"account_ref": acc, "reason": row.get("reason", "")})

    created = 0
    for entry in entries:
        try:
            await flag_account(
                entry["account_ref"],
                reason=entry.get("reason", ""),
                severity=severity,
                source=source,
                flagged_by="import",
            )
            created += 1
        except Exception:  # noqa: BLE001
            continue
    return {"imported": created, "total": len(entries)}