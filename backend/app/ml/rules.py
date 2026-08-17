"""Transparent rule engine for FFMitra.

Every rule returns (name, severity, weight, description). The aggregate rule
score (0..1) combines weighted hits; hard rules (watchlist) short-circuit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SEVERITY_WEIGHT = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 1.0}


@dataclass
class RuleHit:
    name: str
    severity: str
    weight: float = 0.0
    description: str = ""
    hard_block: bool = False
    fields: dict = field(default_factory=dict)


def _amount(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def evaluate_rules(
    tx: dict,
    features: dict,
    watchlist_hit: bool = False,
) -> list[RuleHit]:
    """Evaluate all rules against a transaction.

    tx: raw transaction dict (amount, channel, device_id, location, source_ref,
        dest_ref, txn_time, merchant).
    features: the named feature dict (from features.compute_features zipped with
        FEATURES names).
    watchlist_hit: True if source or dest account is on the watchlist/blacklist.
    """
    amount = _amount(tx.get("amount"))
    hour = int(features.get("hour", 0))
    hits: list[RuleHit] = []

    if watchlist_hit:
        hits.append(
            RuleHit(
                name="WATCHLIST_HIT",
                severity="HIGH",
                weight=1.0,
                description="Source or destination account is on the flagged watchlist.",
                hard_block=True,
                fields={"account_ref": tx.get("dest_ref") or tx.get("source_ref")},
            )
        )

    if amount >= 100_000:
        hits.append(RuleHit("HIGH_AMOUNT", "HIGH", 0.9, "Amount exceeds ₹1,00,000 threshold."))
    elif amount >= 50_000:
        hits.append(RuleHit("HIGH_AMOUNT", "MEDIUM", 0.5, "Amount above ₹50,000 threshold."))

    if features.get("round_amount", 0) == 1:
        hits.append(RuleHit("ROUND_AMOUNT", "LOW", 0.2, "Round / suspicious amount pattern."))

    if features.get("velocity_spike", 0) >= 3:
        hits.append(
            RuleHit(
                "VELOCITY_SPIKE",
                "MEDIUM",
                0.55,
                "Transaction frequency well above the account baseline (velocity burst).",
            )
        )

    if features.get("new_device", 0) == 1 and amount > 20_000:
        hits.append(
            RuleHit(
                "NEW_DEVICE_HIGH_VALUE",
                "HIGH",
                0.8,
                "High-value transaction from an unrecognized device.",
            )
        )

    if features.get("new_location", 0) == 1 and features.get("distance_km", 0) > 500:
        hits.append(
            RuleHit(
                "NEW_LOCATION_FAR",
                "MEDIUM",
                0.55,
                "Transaction from a new, far-away location.",
            )
        )

    if features.get("midnight_txn", 0) == 1 and amount > 10_000:
        hits.append(
            RuleHit(
                "MIDNIGHT_HIGH_VALUE",
                "MEDIUM",
                0.5,
                "Unusually large transaction during late-night hours.",
            )
        )

    if 0 < amount < 10:
        hits.append(
            RuleHit(
                "MICRO_TEST_AMOUNT",
                "MEDIUM",
                0.6,
                "Micro amount — classic 'test before big theft' scam signature.",
            )
        )

    if features.get("first_txn_of_day", 0) == 1 and amount > 20_000:
        hits.append(
            RuleHit(
                "FIRST_TXN_HIGH",
                "LOW",
                0.35,
                "High amount on first transaction of the day.",
            )
        )

    if features.get("counterparty_count_24h", 0) >= 8:
        hits.append(
            RuleHit(
                "COUNTERPARTY_CONCENTRATION",
                "LOW",
                0.35,
                "Many distinct counterparties in 24h (layering pattern).",
            )
        )

    if features.get("amount_ratio", 0) >= 10:
        hits.append(
            RuleHit(
                "AMOUNT_ESCALATION",
                "HIGH",
                0.75,
                "Amount is many times larger than the account's normal spend.",
            )
        )

    if features.get("is_cross_bank", 0) == 1 and amount > 30_000:
        hits.append(
            RuleHit(
                "CROSS_BANK_HIGH",
                "LOW",
                0.3,
                "Large inter-bank transfer at elevated risk.",
            )
        )

    return hits


def rule_score(hits: list[RuleHit]) -> float:
    """Aggregate rule hits into a 0..1 score (no hard blocks)."""
    if not hits:
        return 0.0
    hard = any(h.hard_block for h in hits)
    if hard:
        return 1.0
    raw = sum(SEVERITY_WEIGHT[h.severity] * h.weight for h in hits)
    return min(raw, 1.0)