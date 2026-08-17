"""Dashboard statistics endpoints."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..auth import get_current_user
from ..db import get_db
from ..services import simulator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(_user: dict = Depends(get_current_user)) -> dict:
    db = get_db()
    recent = await db.select("transactions", order="txn_time.desc", limit=500)
    alerts = await db.select("alerts", order="created_at.desc", limit=200)
    flagged = await db.select("flagged_accounts", {"active": "true"}, limit=100)

    decisions = Counter(t.get("risk_decision", "APPROVE") for t in recent)
    total_amount = sum(float(t.get("amount") or 0) for t in recent)
    channels = Counter(t.get("channel", "UPI") for t in recent)

    hourly: dict[str, int] = defaultdict(int)
    for t in recent:
        bucket = (t.get("txn_time") or "")[:13] + ":00"
        hourly[bucket] += 1
    series = [
        {"bucket": k, "count": hourly[k]}
        for k in sorted(hourly)[-24:]
    ]

    alert_types = Counter(a.get("alert_type", "UNKNOWN") for a in alerts)
    severity = Counter(a.get("severity", "LOW") for a in alerts)

    risk_dist = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for t in recent:
        s = float(t.get("risk_score") or 0)
        if s <= 20:
            risk_dist["0-20"] += 1
        elif s <= 40:
            risk_dist["21-40"] += 1
        elif s <= 60:
            risk_dist["41-60"] += 1
        elif s <= 80:
            risk_dist["61-80"] += 1
        else:
            risk_dist["81-100"] += 1

    return {
        "kpis": {
            "transactions": len(recent),
            "blocked": decisions.get("BLOCK", 0),
            "review": decisions.get("REVIEW", 0),
            "approved": decisions.get("APPROVE", 0),
            "total_volume": round(total_amount, 2),
            "alerts": len(alerts),
            "open_alerts": sum(1 for a in alerts if not a.get("acknowledged")),
            "flagged_accounts": len(flagged),
        },
        "decisions": dict(decisions),
        "channels": dict(channels),
        "hourly": series,
        "alert_types": dict(alert_types),
        "severity": dict(severity),
        "risk_distribution": risk_dist,
        "simulator": simulator.simulator_status(),
    }


@router.get("/live")
async def live_transactions(
    limit: int = Query(30, ge=1, le=200), _user: dict = Depends(get_current_user)
) -> dict:
    db = get_db()
    rows = await db.select("transactions", order="txn_time.desc", limit=limit)
    return {"transactions": rows}