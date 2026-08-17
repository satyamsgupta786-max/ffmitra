"""Enforcement: watchlist/blacklist checks, auto-block, alert generation, persistence."""

from __future__ import annotations

import time
from typing import Optional

from ..db import get_db
from ..ml.scorer import ScoreResult

ALERT_TYPES = {
    "AUTO_BLOCK": "Transaction blocked automatically",
    "FRAUD_SCORE": "High risk transaction flagged",
    "WATCHLIST_HIT": "Flagged account involved",
    "ANOMALY": "Anomalous pattern detected",
    "REVIEW_QUEUE": "Transaction moved to review queue",
}


async def is_flagged(account_ref: Optional[str]) -> bool:
    if not account_ref:
        return False
    try:
        db = get_db()
        row = await db.get_one("flagged_accounts", {"account_ref": account_ref, "active": "true"})
        return row is not None
    except Exception:  # noqa: BLE001
        return False


async def flag_account(
    account_ref: str,
    reason: str = "",
    severity: str = "HIGH",
    source: str = "MANUAL",
    flagged_by: str = "system",
) -> dict:
    db = get_db()
    rows = await db.insert(
        "flagged_accounts",
        [
            {
                "account_ref": account_ref,
                "reason": reason,
                "severity": severity,
                "source": source,
                "flagged_by": flagged_by,
            }
        ],
        on_conflict="account_ref",
        upsert=True,
    )
    await db.update("accounts", {"account_ref": account_ref}, {"flagged": True})
    return rows[0] if rows else {"account_ref": account_ref}


async def unflag_account(account_ref: str) -> None:
    db = get_db()
    await db.update("flagged_accounts", {"account_ref": account_ref}, {"active": False})
    await db.update("accounts", {"account_ref": account_ref}, {"flagged": False})


async def create_alert(
    alert_type: str,
    severity: str,
    title: str,
    description: str = "",
    txn_ref: Optional[str] = None,
    account_ref: Optional[str] = None,
) -> dict:
    db = get_db()
    rows = await db.insert(
        "alerts",
        [
            {
                "alert_type": alert_type,
                "severity": severity,
                "title": title,
                "description": description,
                "txn_ref": txn_ref,
                "account_ref": account_ref,
            }
        ],
    )
    return rows[0] if rows else {}


def _severity_for(risk_score: float) -> str:
    if risk_score >= 85:
        return "HIGH"
    if risk_score >= 60:
        return "MEDIUM"
    return "LOW"


async def store_transaction(tx: dict, result: ScoreResult) -> dict:
    """Persist a scored transaction and raise alerts for BLOCK / high risk."""
    db = get_db()
    row = {
        "txn_ref": result.txn_ref,
        "source_ref": tx.get("source_ref", ""),
        "dest_ref": tx.get("dest_ref", ""),
        "amount": float(tx.get("amount") or 0),
        "currency": tx.get("currency", "INR"),
        "channel": tx.get("channel", "UPI"),
        "txn_type": tx.get("txn_type", "P2P"),
        "txn_time": tx.get("txn_time") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device_id": tx.get("device_id"),
        "ip_address": tx.get("ip_address"),
        "location": tx.get("location"),
        "merchant": tx.get("merchant"),
        "risk_score": result.risk_score,
        "risk_decision": result.decision,
        "risk_reasons": result.reasons,
        "is_fraud": result.decision == "BLOCK",
        "is_reviewed": False,
        "meta": {
            "ml_probability": result.ml_probability,
            "anomaly_score": result.anomaly_score,
            "rule_score": result.rule_score,
            "rules": result.rules,
            "shap": result.shap_values,
        },
    }
    try:
        stored = await db.insert("transactions", [row], on_conflict="txn_ref", upsert=True)
    except Exception:  # noqa: BLE001
        return row

    severity = _severity_for(result.risk_score)
    if result.decision == "BLOCK":
        await create_alert(
            "AUTO_BLOCK",
            severity,
            ALERT_TYPES["AUTO_BLOCK"],
            f"{result.txn_ref} blocked at risk {result.risk_score:.0f}. {result.reasons[0] if result.reasons else ''}",
            txn_ref=result.txn_ref,
            account_ref=tx.get("source_ref"),
        )
    elif result.decision == "REVIEW":
        await create_alert(
            "REVIEW_QUEUE",
            severity,
            ALERT_TYPES["REVIEW_QUEUE"],
            f"{result.txn_ref} queued for review at risk {result.risk_score:.0f}.",
            txn_ref=result.txn_ref,
            account_ref=tx.get("source_ref"),
        )

    try:
        await db.update(
            "accounts",
            {"account_ref": tx.get("source_ref", "")},
            {"risk_score": result.risk_score, "flagged": True if result.decision == "BLOCK" else None},
        )
    except Exception:  # noqa: BLE001
        pass
    return stored[0] if stored else row


async def ensure_account(tx: dict) -> None:
    """Create account rows for unknown parties so profiles build up over time."""
    db = get_db()
    try:
        existing = await db.select("accounts", {"account_ref": tx.get("source_ref", "")}, limit=1)
        if not existing:
            await db.insert(
                "accounts",
                [
                    {
                        "account_ref": tx.get("source_ref", ""),
                        "account_type": "UPI",
                        "holder_name": tx.get("source_ref", ""),
                        "bank": "UNKNOWN",
                    }
                ],
            )
    except Exception:  # noqa: BLE001
        pass