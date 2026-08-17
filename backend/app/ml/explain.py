"""SHAP-based per-transaction explanation (tree explainer, single-row)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from .loader import get_bundle

_FEATURE_LABELS = {
    "amount": "Transaction amount",
    "hour": "Hour of day",
    "is_weekend": "Weekend transaction",
    "is_night": "Late-night transaction",
    "txn_count_1h": "Transactions in last hour",
    "txn_count_24h": "Transactions in last 24h",
    "sum_amount_1h": "Sum sent in last hour",
    "sum_amount_24h": "Sum sent in last 24h",
    "avg_amount_24h": "Average amount (24h)",
    "amount_ratio": "Amount vs account average",
    "velocity_spike": "Velocity spike",
    "new_device": "New device",
    "new_location": "New location",
    "round_amount": "Round amount pattern",
    "distance_km": "Distance from usual location",
    "account_age_days": "Account age",
    "counterparty_count_24h": "Distinct recipients (24h)",
    "amount_stdev_24h": "Amount volatility (24h)",
    "frequency_ratio": "Frequency vs baseline",
    "first_txn_of_day": "First transaction of day",
    "midnight_txn": "Midnight transaction",
    "is_cross_bank": "Cross-bank transfer",
}

_explainer: Optional[object] = None


def _get_explainer():
    global _explainer
    if _explainer is None:
        try:
            import shap

            bundle = get_bundle()
            _explainer = shap.TreeExplainer(bundle.xgb)
        except Exception:  # noqa: BLE001
            _explainer = False
    return _explainer or None


def explain_shap(feature_row: list[float], named: dict) -> list[dict]:
    """Return top positive-contribution features as {feature, label, value, impact}."""
    explainer = _get_explainer()
    if explainer is None:
        return []
    try:
        row = np.asarray(feature_row, dtype=np.float64).reshape(1, -1)
        values = explainer.shap_values(row)
        if isinstance(values, list):
            values = values[-1]
        contributions = np.asarray(values).ravel()
        order = np.argsort(np.abs(contributions))[::-1][:5]
        result = []
        for idx in order:
            feature = get_bundle().features[idx]
            result.append(
                {
                    "feature": feature,
                    "label": _FEATURE_LABELS.get(feature, feature),
                    "value": round(float(named.get(feature, 0.0)), 4),
                    "impact": round(float(contributions[idx]), 4),
                }
            )
        return result
    except Exception:  # noqa: BLE001
        return []