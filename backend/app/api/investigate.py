"""Investigation endpoints: account profile + fund-trail graph."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_current_user
from ..db import get_db
from ..graph.fundtrail import build_fund_trail

router = APIRouter(prefix="/api/investigate", tags=["investigate"])


@router.get("/account/{account_ref}")
async def account_profile(account_ref: str, _user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    account = await db.get_one("accounts", {"account_ref": account_ref})
    sent = await db.select(
        "transactions", {"source_ref": account_ref}, order="txn_time.desc", limit=300
    )
    received = await db.select(
        "transactions", {"dest_ref": account_ref}, order="txn_time.desc", limit=300
    )
    if not account and not sent and not received:
        raise HTTPException(404, f"no activity found for account {account_ref}")

    all_txns = sorted(
        sent + received, key=lambda t: t.get("txn_time") or "", reverse=True
    )
    total_sent = sum(float(t["amount"]) for t in sent)
    total_received = sum(float(t["amount"]) for t in received)
    counterparties: Counter = Counter()
    devices: Counter = Counter()
    locations: Counter = Counter()
    decisions: Counter = Counter()
    for t in all_txns:
        counterparties[t["dest_ref"] if t["source_ref"] == account_ref else t["source_ref"]] += 1
        if t.get("device_id"):
            devices[t["device_id"]] += 1
        if t.get("location"):
            locations[t["location"]] += 1
        decisions[t.get("risk_decision", "APPROVE")] += 1

    buckets: dict[str, dict] = defaultdict(lambda: {"count": 0, "sum": 0.0, "risk": []})
    for t in all_txns:
        ts = (t.get("txn_time") or "")[:13] + ":00:00"
        buckets[ts]["count"] += 1
        buckets[ts]["sum"] += float(t["amount"])
        buckets[ts]["risk"].append(float(t.get("risk_score") or 0))
    trend = [
        {
            "bucket": k,
            "count": v["count"],
            "sum": round(v["sum"], 2),
            "avg_risk": round(sum(v["risk"]) / len(v["risk"]), 2) if v["risk"] else 0,
        }
        for k, v in sorted(buckets.items())
    ][-48:]

    flagged_row = await db.get_one("flagged_accounts", {"account_ref": account_ref, "active": "true"})

    return {
        "account": account or {"account_ref": account_ref, "account_type": "UNKNOWN", "bank": "UNKNOWN"},
        "flagged": flagged_row,
        "stats": {
            "total_sent": round(total_sent, 2),
            "total_received": round(total_received, 2),
            "txn_count": len(all_txns),
            "outgoing": len(sent),
            "incoming": len(received),
            "top_counterparties": counterparties.most_common(10),
            "devices": devices.most_common(10),
            "locations": locations.most_common(10),
            "decisions": dict(decisions),
        },
        "trend": trend,
        "recent_transactions": all_txns[:100],
    }


@router.get("/fundtrail/{account_ref}")
async def fund_trail(
    account_ref: str,
    depth: int = Query(2, ge=1, le=3),
    _user: dict = Depends(get_current_user),
) -> dict:
    return await build_fund_trail(account_ref, depth=depth)