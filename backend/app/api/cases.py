"""Case management endpoints (victim reports, analyst review)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_current_user
from ..db import get_db
from ..schemas import CaseIn, CaseNoteIn, CaseUpdateIn

router = APIRouter(prefix="/api/cases", tags=["cases"])


async def _next_case_no(db) -> str:
    rows = await db.select("cases", columns="case_no", order="case_no.desc", limit=1)
    if rows:
        try:
            n = int(rows[0]["case_no"].rsplit("-", 1)[1]) + 1
        except (ValueError, IndexError):
            n = 1
    else:
        n = 1
    return f"FMC-{n:04d}"


@router.get("")
async def list_cases(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    _user: dict = Depends(get_current_user),
) -> dict:
    db = get_db()
    filters: dict = {}
    if status:
        filters["status"] = status
    if category:
        filters["category"] = category
    rows = await db.select("cases", filters, order="created_at.desc", limit=limit)
    return {"cases": rows, "count": len(rows)}


@router.post("")
async def create_case(case: CaseIn, user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    case_no = await _next_case_no(db)
    rows = await db.insert(
        "cases",
        [
            {
                "case_no": case_no,
                "title": case.title,
                "category": case.category,
                "status": "OPEN",
                "summary": case.summary,
                "victim_name": case.victim_name,
                "victim_contact": case.victim_contact,
                "source": case.source,
                "created_by": user.get("email") or "system",
            }
        ],
    )
    return rows[0]


@router.get("/{case_id}")
async def get_case(case_id: int, _user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    rows = await db.select("cases", {"id": str(case_id)}, limit=1)
    if not rows:
        raise HTTPException(404, "case not found")
    notes = await db.select("case_notes", {"case_id": str(case_id)}, order="created_at.desc", limit=100)
    return {**rows[0], "notes": notes}


@router.patch("/{case_id}")
async def update_case(
    case_id: int, body: CaseUpdateIn, _user: dict = Depends(get_current_user)
) -> dict:
    db = get_db()
    values = body.model_dump(exclude_none=True)
    if not values:
        raise HTTPException(400, "nothing to update")
    rows = await db.update("cases", {"id": str(case_id)}, values)
    if not rows:
        raise HTTPException(404, "case not found")
    return rows[0]


@router.post("/{case_id}/notes")
async def add_note(case_id: int, body: CaseNoteIn, user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    rows = await db.insert(
        "case_notes",
        [
            {
                "case_id": case_id,
                "note": body.note,
                "author": user.get("email") or "system",
            }
        ],
    )
    return rows[0] if rows else {"id": None}