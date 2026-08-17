"""Generate synthetic training transactions with encoded fraud patterns.

Deterministic (random.seed(42)). Target ~120k rows, ~3-5% fraud.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "datasets" / "synthetic_transactions.csv"

rng = random.Random(42)

SOURCE_ACCOUNTS = [f"SRC_{i:03d}" for i in range(30)]
DEST_ACCOUNTS = [f"DST_{i:05d}" for i in range(1500)]
MERCHANTS = [f"MERCHANT_{i}" for i in range(40)]
CHANNELS = ["UPI", "IMPS", "NEFT", "CARD", "RTGS"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad"]
CITY_GEO = {
    "Mumbai": (19.076, 72.877),
    "Delhi": (28.704, 77.102),
    "Bangalore": (12.971, 77.594),
    "Pune": (18.520, 73.856),
    "Chennai": (13.083, 80.270),
    "Kolkata": (22.572, 88.364),
    "Hyderabad": (17.385, 78.487),
    "Ahmedabad": (23.022, 72.571),
}
FOREIGN = {"Lagos": (6.524, 3.379), "London": (51.507, -0.128), "Dubai": (25.204, 55.271)}

BASE_START = datetime(2025, 1, 1, 0, 0, 0)
DURATION_DAYS = 90


def haversine_km(a: tuple, b: tuple) -> float:
    from math import asin, cos, radians, sin, sqrt

    lat1, lon1 = radians(a[0]), radians(a[1])
    lat2, lon2 = radians(b[0]), radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(h))


def rand_time(minutes_since_start: int) -> str:
    return (BASE_START + timedelta(minutes=minutes_since_start)).isoformat()


def base_txn(source: str, dest: str, amount: float, t: int, device: str, loc: str, channel: str = "UPI") -> dict:
    return {
        "txn_ref": f"TXN_{rng.randint(0, 999999999):09d}",
        "source_ref": source,
        "dest_ref": dest,
        "amount": round(amount, 2),
        "channel": channel,
        "txn_time": rand_time(t),
        "device_id": device,
        "location": loc,
        "account_age_days": 0,
        "is_fraud": 0,
    }


def pattern_velocity_bursts(out: list[dict]) -> None:
    for _ in range(90):
        source = rng.choice(SOURCE_ACCOUNTS)
        start_t = rng.randint(0, DURATION_DAYS * 1440 - 200)
        n = rng.randint(8, 25)
        device = f"DEV_BURST_{rng.randint(0, 999)}"
        for i in range(n):
            t = start_t + i * rng.randint(1, 4)
            out.append(
                base_txn(
                    source,
                    rng.choice(DEST_ACCOUNTS),
                    round(rng.uniform(500, 5000), 2),
                    t,
                    device,
                    rng.choice(CITIES),
                )
                | {"is_fraud": 1}
            )


def pattern_new_account_high_amount(out: list[dict]) -> None:
    for _ in range(180):
        source = rng.choice(SOURCE_ACCOUNTS)
        day = rng.randint(1, DURATION_DAYS - 1)
        t = day * 1440 + rng.randint(0, 1439)
        amt = rng.uniform(50000, 400000)
        out.append(
            base_txn(
                source,
                rng.choice(DEST_ACCOUNTS),
                amt,
                t,
                f"DEV_NEW_{rng.randint(0, 9999)}",
                rng.choice(CITIES),
                "IMPS",
            )
            | {"account_age_days": rng.randint(1, 5), "is_fraud": 1}
        )


def pattern_round_amount_escalations(out: list[dict]) -> None:
    for _ in range(150):
        source = rng.choice(SOURCE_ACCOUNTS)
        start_t = rng.randint(0, DURATION_DAYS * 1440 - 300)
        device = f"DEV_ROUND_{rng.randint(0, 999)}"
        dest = rng.choice(DEST_ACCOUNTS)
        for base, delay in ((9999, 10), (50000, 20), (100000, 40)):
            out.append(
                base_txn(source, dest, base, start_t + delay, device, rng.choice(CITIES))
                | {"is_fraud": 1}
            )


def pattern_night_high_amount(out: list[dict]) -> None:
    for _ in range(220):
        source = rng.choice(SOURCE_ACCOUNTS)
        day = rng.randint(0, DURATION_DAYS - 1)
        hour = rng.choice([0, 1, 2, 3, 4])
        t = day * 1440 + hour * 60 + rng.randint(0, 59)
        out.append(
            base_txn(
                source,
                rng.choice(DEST_ACCOUNTS),
                rng.uniform(60000, 500000),
                t,
                f"DEV_NIGHT_{rng.randint(0, 999)}",
                rng.choice(CITIES),
                "IMPS",
            )
            | {"is_fraud": 1}
        )


def pattern_mule_chains(out: list[dict]) -> None:
    for _ in range(120):
        source = rng.choice(SOURCE_ACCOUNTS)
        day = rng.randint(0, DURATION_DAYS - 1)
        t = day * 1440 + rng.randint(0, 1439)
        amt = rng.uniform(10000, 200000)
        dest1 = rng.choice(DEST_ACCOUNTS)
        dest2 = rng.choice(DEST_ACCOUNTS)
        device = f"DEV_MULE_{rng.randint(0, 999)}"
        out.append(
            base_txn(source, dest1, amt, t, device, rng.choice(CITIES))
            | {"is_fraud": 1}
        )
        out.append(
            base_txn(dest1, dest2, amt * rng.uniform(0.9, 1.0), t + 5, device, rng.choice(CITIES))
            | {"account_age_days": rng.randint(1, 30), "is_fraud": 1}
        )


def pattern_small_test_then_big_withdraw(out: list[dict]) -> None:
    for _ in range(130):
        source = rng.choice(SOURCE_ACCOUNTS)
        day = rng.randint(0, DURATION_DAYS - 1)
        t = day * 1440 + rng.randint(0, 1439)
        device = f"DEV_TEST_{rng.randint(0, 999)}"
        out.append(
            base_txn(source, rng.choice(DEST_ACCOUNTS), 1.0, t, device, rng.choice(CITIES))
            | {"is_fraud": 1}
        )
        out.append(
            base_txn(
                source,
                rng.choice(DEST_ACCOUNTS),
                rng.uniform(50000, 300000),
                t + rng.randint(15, 90),
                device,
                rng.choice(CITIES),
            )
            | {"is_fraud": 1}
        )


def pattern_new_device_new_location(out: list[dict]) -> None:
    for _ in range(150):
        source = rng.choice(SOURCE_ACCOUNTS)
        day = rng.randint(1, DURATION_DAYS - 1)
        t = day * 1440 + rng.randint(0, 1439)
        home = rng.choice(CITIES)
        geo = CITY_GEO[home]
        far_loc, far_geo = rng.choice(list(FOREIGN.items()))
        km = haversine_km(geo, far_geo)
        out.append(
            base_txn(
                source,
                rng.choice(DEST_ACCOUNTS),
                rng.uniform(50000, 350000),
                t,
                f"DEV_FOREIGN_{rng.randint(0, 9999)}",
                far_loc,
                "CARD",
            )
            | {
                "account_age_days": rng.randint(5, 60),
                "is_fraud": 1,
                "geo": km,
            }
        )


def pattern_counterparty_concentration(out: list[dict]) -> None:
    for _ in range(120):
        source = rng.choice(SOURCE_ACCOUNTS)
        dest = rng.choice(DEST_ACCOUNTS)
        start_t = rng.randint(0, DURATION_DAYS * 1440 - 300)
        device = f"DEV_CONC_{rng.randint(0, 999)}"
        for i in range(rng.randint(10, 20)):
            out.append(
                base_txn(
                    source,
                    dest,
                    round(rng.uniform(1000, 15000), 2),
                    start_t + i * rng.randint(3, 15),
                    device,
                    rng.choice(CITIES),
                )
                | {"is_fraud": 1}
            )


def legit_salary_inflow(out: list[dict]) -> None:
    for source in SOURCE_ACCOUNTS:
        for m in range(DURATION_DAYS // 30):
            day = m * 30 + rng.randint(1, 2)
            t = day * 1440 + 9 * 60 + rng.randint(0, 120)
            out.append(
                base_txn(
                    f"EMPLOYER_{m}",
                    source,
                    rng.uniform(40000, 120000),
                    t,
                    f"DEV_WORK_{rng.randint(0, 99)}",
                    rng.choice(CITIES),
                    "NEFT",
                )
            )


def legit_weekly_shopping(out: list[dict]) -> None:
    for source in SOURCE_ACCOUNTS:
        device = f"DEV_HOME_{source}"
        loc = rng.choice(CITIES)
        for w in range(DURATION_DAYS // 7):
            day = w * 7 + rng.randint(5, 6)
            for _ in range(rng.randint(2, 6)):
                t = day * 1440 + rng.randint(10 * 60, 20 * 60)
                out.append(
                    base_txn(
                        source,
                        rng.choice(MERCHANTS),
                        rng.uniform(200, 8000),
                        t,
                        device,
                        loc,
                        "CARD",
                    )
                )


def legit_small_daily_spends(out: list[dict]) -> None:
    for source in SOURCE_ACCOUNTS:
        device = f"DEV_DAILY_{source}"
        loc = rng.choice(CITIES)
        for day in range(DURATION_DAYS):
            n = rng.randint(20, 60)
            for _ in range(n):
                t = day * 1440 + rng.randint(8 * 60, 22 * 60)
                out.append(
                    base_txn(
                        source,
                        rng.choice(MERCHANTS),
                        rng.uniform(20, 1500),
                        t,
                        device,
                        loc,
                        "UPI",
                    )
                )


def legit_occasional_large(out: list[dict]) -> None:
    for source in SOURCE_ACCOUNTS:
        device = f"DEV_LARGE_{source}"
        loc = rng.choice(CITIES)
        for _ in range(rng.randint(4, 9)):
            day = rng.randint(0, DURATION_DAYS - 1)
            t = day * 1440 + rng.randint(9 * 60, 18 * 60)
            out.append(
                base_txn(
                    source,
                    rng.choice(DEST_ACCOUNTS),
                    rng.uniform(10000, 45000),
                    t,
                    device,
                    loc,
                    rng.choice(["IMPS", "NEFT"]),
                )
            )


def main() -> None:
    rows: list[dict] = []
    pattern_velocity_bursts(rows)
    pattern_new_account_high_amount(rows)
    pattern_round_amount_escalations(rows)
    pattern_night_high_amount(rows)
    pattern_mule_chains(rows)
    pattern_small_test_then_big_withdraw(rows)
    pattern_new_device_new_location(rows)
    pattern_counterparty_concentration(rows)
    legit_salary_inflow(rows)
    legit_weekly_shopping(rows)
    legit_small_daily_spends(rows)
    legit_occasional_large(rows)

    rng.shuffle(rows)
    rows.sort(key=lambda r: (r["source_ref"], r["txn_time"]))

    columns = [
        "txn_ref",
        "source_ref",
        "dest_ref",
        "amount",
        "channel",
        "txn_time",
        "device_id",
        "location",
        "account_age_days",
        "is_fraud",
        "geo",
    ]
    for i, row in enumerate(rows):
        row["txn_ref"] = f"SYN_{i:06d}"

    import csv

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with open(DEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    fraud = sum(1 for r in rows if r["is_fraud"])
    print(f"WROTE {len(rows)} rows -> {DEST}")
    print(f"fraud rows: {fraud} ({100.0 * fraud / len(rows):.2f}%)")


if __name__ == "__main__":
    main()
