"""Transaction scoring, lookup and list endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_current_user
from ..db import get_db
from ..ml.scorer import score_transaction
from ..schemas import ScoreResponse, TxnBatchIn, TxnIn
from ..services.enforcement import is_flagged, store_transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _to_response(tx: dict, result) -> ScoreResponse:
    return ScoreResponse(
        txn_ref=result.txn_ref,
        risk_score=result.risk_score,
        decision=result.decision,
        ml_probability=result.ml_probability,
        anomaly_score=result.anomaly_score,
        rule_score=result.rule_score,
        reasons=result.reasons,
        rules=result.rules,
        shap_values=result.shap_values,
    )


@router.post("/score", response_model=ScoreResponse)
async def score_one(tx: TxnIn, _user: dict = Depends(get_current_user)) -> ScoreResponse:
    flagged = await is_flagged(tx.source_ref) or await is_flagged(tx.dest_ref)
    result = await score_transaction(tx.model_dump(), watchlist_hit=flagged)
    await store_transaction(tx.model_dump(), result)
    return _to_response(tx, result)


@router.post("/batch")
async def score_batch(
    body: TxnBatchIn, _user: dict = Depends(get_current_user)
) -> dict:
    out = []
    for tx in body.transactions:
        flagged = await is_flagged(tx.source_ref) or await is_flagged(tx.dest_ref)
        result = await score_transaction(tx.model_dump(), watchlist_hit=flagged)
        await store_transaction(tx.model_dump(), result)
        out.append(_to_response(tx, result).model_dump())
    return {"scored": len(out), "results": out}


@router.get("")
async def list_transactions(
    q: Optional[str] = Query(None, description="Search by txn ref, source or dest"),
    decision: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _user: dict = Depends(get_current_user),
) -> dict:
    db = get_db()
    filters: dict = {}
    if decision:
        filters["risk_decision"] = decision
    if channel:
        filters["channel"] = channel
    if q:
        rows = await db.select(
            "transactions",
            {"txn_ref": q},
            order="txn_time.desc",
            limit=limit,
            offset=offset,
        )
        if not rows:
            rows = await db.select(
                "transactions",
                {"source_ref": q},
                order="txn_time.desc",
                limit=limit,
                offset=offset,
            )
        if not rows:
            rows = await db.select(
                "transactions",
                {"dest_ref": q},
                order="txn_time.desc",
                limit=limit,
                offset=offset,
            )
        return {"transactions": rows, "count": len(rows)}
    rows = await db.select(
        "transactions", filters, order="txn_time.desc", limit=limit, offset=offset
    )
    total = await db.count("transactions", filters)
    return {"transactions": rows, "count": total}


@router.get("/{txn_ref}")
async def get_transaction(txn_ref: str, _user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    rows = await db.select("transactions", {"txn_ref": txn_ref}, limit=1)
    if not rows:
        raise HTTPException(404, f"transaction {txn_ref} not found")
    return rows[0]