"""Ensemble fraud scorer: ML probability + anomaly + rules -> risk 0..100 and decision."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from ..db import get_db
from .explain import explain_shap
from .features import FEATURES, compute_features
from .loader import get_bundle
from .rules import RuleHit, evaluate_rules, rule_score

DEFAULT_WEIGHTS = {"ml": 0.6, "anomaly": 0.1, "rule": 0.3}

_lock = threading.Lock()
_history: dict[str, list[dict]] = {}
_profiles: dict[str, dict] = {}
_HISTORY_LIMIT = 500


@dataclass
class ScoreResult:
    txn_ref: str
    risk_score: float
    decision: str
    ml_probability: float
    anomaly_score: float
    rule_score: float
    weights: dict
    reasons: list[str] = field(default_factory=list)
    rules: list[dict] = field(default_factory=list)
    features: list[float] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    shap_values: list[dict] = field(default_factory=list)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def remember(tx: dict) -> None:
    """Keep a rolling per-account history window for real-time feature engineering."""
    src = tx.get("source_ref")
    if not src:
        return
    with _lock:
        window = _history.setdefault(src, [])
        window.append(tx)
        if len(window) > _HISTORY_LIMIT:
            del window[: len(window) - _HISTORY_LIMIT]


async def _load_profile(source_ref: str, dest_ref: str, tx: dict) -> dict:
    """Build the profile dict for feature engineering (DB-backed, cached in memory)."""
    with _lock:
        cached = _profiles.get(source_ref)
    if cached is not None:
        return cached

    profile = {
        "account_age_days": 365.0,
        "expected_daily": 10.0,
        "geo": 0.0,
        "cross_bank": 0,
        "counterparty_map": {},
    }
    try:
        db = get_db()
        account = await db.get_one("accounts", {"account_ref": source_ref})
        if account:
            profile["account_age_days"] = 365.0
            if account.get("created_at"):
                try:
                    from datetime import datetime, timezone

                    created = datetime.fromisoformat(account["created_at"].replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - created).days
                    profile["account_age_days"] = float(max(age, 0))
                except Exception:  # noqa: BLE001
                    pass
            profile["cross_bank"] = 1
        history = await db.select(
            "transactions",
            {"source_ref": source_ref},
            columns="dest_ref,txn_time,amount,device_id,location",
            order="txn_time.desc",
            limit=100,
        )
        if history:
            from .features import _as_dt

            txn_time = tx.get("txn_time") or _now_iso()
            t_float = _as_dt(txn_time).timestamp()
            cutoff_24h = t_float - 86400.0
            recent = [h for h in history if _as_dt(h.get("txn_time")).timestamp() >= cutoff_24h]
            if recent:
                profile["expected_daily"] = max(len(recent), 1)
                profile["counterparty_map"] = {}
                for h in recent:
                    d = h.get("dest_ref")
                    profile["counterparty_map"][d] = profile["counterparty_map"].get(d, 0) + 1
    except Exception:  # noqa: BLE001
        pass

    with _lock:
        _profiles[source_ref] = profile
    return profile


async def score_transaction(
    tx: dict,
    weights: Optional[dict] = None,
    watchlist_hit: bool = False,
    use_explain: bool = True,
) -> ScoreResult:
    """Score a single transaction end-to-end. tx must include txn_ref."""
    weights = weights or DEFAULT_WEIGHTS
    txn_ref = tx.get("txn_ref") or f"TX-{int(time.time() * 1000)}"
    tx = {**tx, "txn_ref": txn_ref}

    profile = await _load_profile(tx.get("source_ref"), tx.get("dest_ref"), tx)
    with _lock:
        history = list(_history.get(tx.get("source_ref") or "", []))

    feature_row = compute_features(tx, history, profile)
    named = dict(zip(FEATURES, feature_row))

    ml_p = 0.0
    anomaly = 0.0
    try:
        bundle = get_bundle()
        ml_p = bundle.predict_proba(feature_row)
        anomaly = bundle.anomaly_score(feature_row)
    except FileNotFoundError:
        ml_p = 0.0
        anomaly = 0.0

    hits = evaluate_rules(tx, named, watchlist_hit=watchlist_hit)
    r_score = rule_score(hits)
    hard_block = any(h.hard_block for h in hits)

    score = (
        weights.get("ml", 0.6) * ml_p
        + weights.get("anomaly", 0.1) * anomaly
        + weights.get("rule", 0.3) * r_score
    )
    risk = min(score, 1.0) * 100.0
    if hard_block:
        risk = 99.9
        decision = "BLOCK"
    else:
        threshold_block = 0.85
        threshold_review = 0.6
        try:
            threshold_block = get_bundle().threshold_block()
            threshold_review = get_bundle().threshold_review()
        except FileNotFoundError:
            pass
        if risk >= threshold_block * 100:
            decision = "BLOCK"
        elif risk >= threshold_review * 100:
            decision = "REVIEW"
        else:
            decision = "APPROVE"

    reasons = []
    if ml_p >= 0.7:
        reasons.append(f"ML model flagged high fraud probability ({ml_p:.2f}).")
    elif ml_p >= 0.5:
        reasons.append(f"ML model raised fraud probability ({ml_p:.2f}).")
    if anomaly >= 0.7:
        reasons.append("Anomaly detector found an out-of-profile pattern.")
    for hit in hits:
        reasons.append(hit.description)

    shap_values: list[dict] = []
    if use_explain and ml_p > 0.2:
        try:
            shap_values = explain_shap(feature_row, named)
        except Exception:  # noqa: BLE001
            shap_values = []

    remember(tx)

    return ScoreResult(
        txn_ref=txn_ref,
        risk_score=round(risk, 2),
        decision=decision,
        ml_probability=round(ml_p, 4),
        anomaly_score=round(anomaly, 4),
        rule_score=round(r_score, 4),
        weights=weights,
        reasons=reasons,
        rules=[{"name": h.name, "severity": h.severity, "description": h.description} for h in hits],
        features=feature_row,
        feature_names=FEATURES,
        shap_values=shap_values,
    )


def clear_cache() -> None:
    with _lock:
        _history.clear()
        _profiles.clear()