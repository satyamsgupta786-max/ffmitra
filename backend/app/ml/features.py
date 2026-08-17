"""Feature engineering for FFMitra fraud detection.

The exact 22-feature contract consumed by the live scorer (see loader.py).
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd

FEATURES: List[str] = [
    "amount",
    "hour",
    "is_weekend",
    "is_night",
    "txn_count_1h",
    "txn_count_24h",
    "sum_amount_1h",
    "sum_amount_24h",
    "avg_amount_24h",
    "amount_ratio",
    "velocity_spike",
    "new_device",
    "new_location",
    "round_amount",
    "distance_km",
    "account_age_days",
    "counterparty_count_24h",
    "amount_stdev_24h",
    "frequency_ratio",
    "first_txn_of_day",
    "midnight_txn",
    "is_cross_bank",
]

FEATURE_COLUMNS: List[str] = FEATURES

HOUR_24H = 24 * 3600.0
HOUR_1H = 3600.0

_ROUND_BASE_AMOUNTS = [9999.0, 50000.0, 100000.0]
_DEFAULT_EXPECTED_DAILY = 10.0


def _as_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, np.datetime64):
        return value.astype("M8[ms]").astype(datetime)
    return datetime.fromisoformat(str(value))


def _amount(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def _is_round_amount(amount: float) -> int:
    if amount < 10.0 or amount % 1000.0 == 0.0:
        return 1
    for base in _ROUND_BASE_AMOUNTS:
        for mult in (1, 2, 3, 5, 10):
            if amount >= base - 10.0 and amount <= base * mult + 10.0 and (amount % 100.0) == 0.0:
                return 1
    return 0


def compute_features(tx: dict, history: list[dict], profile: dict) -> list[float]:
    """Compute the 22-feature vector for a single transaction.

    tx: raw txn dict with keys amount, channel, txn_time (ISO str or datetime),
        device_id, location, source_ref, dest_ref, merchant, ip_address.
    history: prior txns of the same source account (any order; sorted internally).
    profile: {account_age_days, counterparty_map, expected_daily, geo, cross_bank}.
    """
    amount = max(_amount(tx.get("amount")), 0.0)
    tx_time = _as_dt(tx.get("txn_time") or datetime.now())
    hour = tx_time.hour

    ordered = sorted(history, key=lambda h: _as_dt(h.get("txn_time") or tx_time))
    t_float = tx_time.timestamp()

    def within(seconds: float) -> list[dict]:
        cutoff = t_float - seconds
        return [h for h in ordered if _as_dt(h.get("txn_time") or tx_time).timestamp() >= cutoff]

    hist_1h = within(HOUR_1H)
    hist_24h = within(HOUR_24H)

    txn_count_1h = float(len(hist_1h))
    txn_count_24h = float(len(hist_24h))
    sum_amount_1h = float(sum(max(_amount(h.get("amount")), 0.0) for h in hist_1h))
    sum_amount_24h = float(sum(max(_amount(h.get("amount")), 0.0) for h in hist_24h))
    avg_amount_24h = sum_amount_24h / txn_count_24h if txn_count_24h > 0 else 0.0
    amount_ratio = amount / (avg_amount_24h + 1.0)
    expected_1h = txn_count_24h / 24.0
    velocity_spike = txn_count_1h / (expected_1h + 0.5)

    known_devices = {h.get("device_id") for h in history}
    known_locations = {h.get("location") for h in history}
    new_device = 0 if tx.get("device_id") in known_devices else 1
    new_location = 0 if tx.get("location") in known_locations else 1

    round_amount = float(_is_round_amount(amount))
    distance_km = float(profile.get("geo", 0.0) or 0.0)
    account_age_days = float(profile.get("account_age_days", 0.0) or 0.0)

    counterparty_map = profile.get("counterparty_map") or {}
    if counterparty_map:
        counterparty_count_24h = float(counterparty_map.get(tx.get("dest_ref"), 0) or 0)
    else:
        counterparty_count_24h = float(len({h.get("dest_ref") for h in hist_24h}))

    if txn_count_24h >= 2:
        amounts_24h = [max(_amount(h.get("amount")), 0.0) for h in hist_24h]
        mean_24h = sum(amounts_24h) / len(amounts_24h)
        amount_stdev_24h = math.sqrt(
            sum((a - mean_24h) ** 2 for a in amounts_24h) / len(amounts_24h)
        )
    else:
        amount_stdev_24h = 0.0

    expected_daily = float(profile.get("expected_daily", _DEFAULT_EXPECTED_DAILY))
    frequency_ratio = txn_count_24h / expected_daily if expected_daily > 0 else 0.0

    first_txn_of_day = 0 if any(
        _as_dt(h.get("txn_time") or tx_time).date() == tx_time.date() for h in history
    ) else 1

    midnight_txn = 1.0 if hour in (0, 1, 2, 3, 4) else 0.0
    is_cross_bank = 1.0 if profile.get("cross_bank") else 0.0

    return [
        amount,
        float(hour),
        float(tx_time.weekday() >= 5),
        1.0 if (hour < 6 or hour > 22) else 0.0,
        txn_count_1h,
        txn_count_24h,
        sum_amount_1h,
        sum_amount_24h,
        avg_amount_24h,
        amount_ratio,
        velocity_spike,
        float(new_device),
        float(new_location),
        round_amount,
        distance_km,
        account_age_days,
        counterparty_count_24h,
        amount_stdev_24h,
        frequency_ratio,
        float(first_txn_of_day),
        midnight_txn,
        is_cross_bank,
    ]


def _group_keys(df: pd.DataFrame) -> list[tuple[str, list[int]]]:
    df = df.sort_values(["source_ref", "txn_time"]).reset_index(drop=True)
    start = 0
    groups: list[tuple[str, list[int]]] = []
    current = None
    for i, row in enumerate(df.itertuples(index=False)):
        key = getattr(row, "source_ref")
        if key != current:
            if current is not None:
                groups.append((current, list(range(start, i))))
            current = key
            start = i
    if current is not None:
        groups.append((current, list(range(start, len(df)))))
    return groups


def build_training_frame(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw transaction rows into the 22-feature frame plus target.

    Requires columns: source_ref, dest_ref, amount, txn_time, device_id,
    location, account_age_days, is_fraud. Rows are grouped per source account
    in time order and each row's features are computed from its prior rows.
    """
    df = transactions_df.copy()
    required = [
        "source_ref",
        "dest_ref",
        "amount",
        "txn_time",
        "device_id",
        "location",
        "account_age_days",
        "is_fraud",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")

    df = df.sort_values(["source_ref", "txn_time"]).reset_index(drop=True)
    if "expected_daily" not in df.columns:
        df["expected_daily"] = _DEFAULT_EXPECTED_DAILY
    if "cross_bank" not in df.columns:
        df["cross_bank"] = 0
    if "geo" not in df.columns:
        df["geo"] = 0.0
    if "channel" not in df.columns:
        df["channel"] = "upip"

    df["txn_time_dt"] = df["txn_time"].map(_as_dt)

    rng = random.Random(42)
    for col in ("expected_daily", "cross_bank", "geo"):
        if df[col].dtype.kind not in "biuf":
            df[col] = df[col].map(lambda v: int(v) if str(v).strip() in ("0", "1") else 0)

    grouped = df.groupby("source_ref", sort=False)

    result_arrays: dict[str, list] = {f: [] for f in FEATURES}
    result_arrays["is_fraud"] = []

    for source, g in grouped:
        g = g.sort_values("txn_time_dt")
        history: list[dict] = []
        for row in g.itertuples(index=False):
            txn_time = row.txn_time_dt
            t_float = txn_time.timestamp()
            cutoff = t_float - HOUR_24H
            history = [h for h in history if h["t"] >= cutoff]

            hist_1h = [h for h in history if h["t"] >= t_float - HOUR_1H]

            amount = max(float(row.amount), 0.0)
            hour = txn_time.hour

            txn_count_1h = float(len(hist_1h))
            txn_count_24h = float(len(history))
            sum_amount_1h = sum(h["amount"] for h in hist_1h)
            sum_amount_24h = sum(h["amount"] for h in history)
            avg_amount_24h = sum_amount_24h / txn_count_24h if txn_count_24h > 0 else 0.0
            amount_ratio = amount / (avg_amount_24h + 1.0)
            expected_1h = txn_count_24h / 24.0
            velocity_spike = txn_count_1h / (expected_1h + 0.5)

            new_device = 0 if row.device_id in {h["device_id"] for h in history} else 1
            new_location = 0 if row.location in {h["location"] for h in history} else 1
            round_amount = float(_is_round_amount(amount))
            distance_km = float(row.geo) if row.geo else 0.0
            account_age_days = float(row.account_age_days) if row.account_age_days else 0.0

            if txn_count_24h >= 2:
                amts = [h["amount"] for h in history]
                mean = sum(amts) / len(amts)
                amount_stdev_24h = math.sqrt(sum((a - mean) ** 2 for a in amts) / len(amts))
            else:
                amount_stdev_24h = 0.0

            expected_daily = float(row.expected_daily)
            frequency_ratio = txn_count_24h / expected_daily if expected_daily > 0 else 0.0

            first_txn_of_day = 0 if any(h["d"] == txn_time.date() for h in history) else 1
            midnight_txn = 1.0 if hour in (0, 1, 2, 3, 4) else 0.0
            is_cross_bank = 1.0 if int(row.cross_bank) else 0.0

            history.append(
                {
                    "t": t_float,
                    "d": txn_time.date(),
                    "amount": amount,
                    "device_id": row.device_id,
                    "location": row.location,
                    "dest_ref": row.dest_ref,
                }
            )

            result_arrays["is_fraud"].append(int(row.is_fraud))
            result_arrays["amount"].append(math.log1p(amount))
            result_arrays["hour"].append(float(hour))
            result_arrays["is_weekend"].append(float(txn_time.weekday() >= 5))
            result_arrays["is_night"].append(1.0 if (hour < 6 or hour > 22) else 0.0)
            result_arrays["txn_count_1h"].append(txn_count_1h)
            result_arrays["txn_count_24h"].append(txn_count_24h)
            result_arrays["sum_amount_1h"].append(math.log1p(sum_amount_1h))
            result_arrays["sum_amount_24h"].append(math.log1p(sum_amount_24h))
            result_arrays["avg_amount_24h"].append(math.log1p(avg_amount_24h))
            result_arrays["amount_ratio"].append(amount_ratio)
            result_arrays["velocity_spike"].append(velocity_spike)
            result_arrays["new_device"].append(float(new_device))
            result_arrays["new_location"].append(float(new_location))
            result_arrays["round_amount"].append(round_amount)
            result_arrays["distance_km"].append(distance_km)
            result_arrays["account_age_days"].append(account_age_days)
            result_arrays["counterparty_count_24h"].append(
                float(len({h["dest_ref"] for h in history}))
            )
            result_arrays["amount_stdev_24h"].append(amount_stdev_24h)
            result_arrays["frequency_ratio"].append(frequency_ratio)
            result_arrays["first_txn_of_day"].append(float(first_txn_of_day))
            result_arrays["midnight_txn"].append(midnight_txn)
            result_arrays["is_cross_bank"].append(is_cross_bank)

    frame = pd.DataFrame(result_arrays)
    frame = frame[FEATURES + ["is_fraud"]]

    numeric_cols = [
        c
        for c in FEATURES
        if c
        not in (
            "hour",
            "is_weekend",
            "is_night",
            "new_device",
            "new_location",
            "round_amount",
            "first_txn_of_day",
            "midnight_txn",
            "is_cross_bank",
        )
    ]
    noise_map = {c: 1.0 + rng.uniform(-0.005, 0.005) for c in numeric_cols}
    for col in numeric_cols:
        if frame[col].nunique(dropna=False) > 1:
            frame[col] = frame[col] * noise_map[col]
        frame[col] = frame[col].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    for col in (
        "hour",
        "is_weekend",
        "is_night",
        "new_device",
        "new_location",
        "round_amount",
        "first_txn_of_day",
        "midnight_txn",
        "is_cross_bank",
    ):
        frame[col] = frame[col].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return frame
