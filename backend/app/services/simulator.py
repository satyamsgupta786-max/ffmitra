"""Real-time transaction simulator: streams realistic UPI/payment traffic through the scorer."""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..db import get_db
from ..ml.scorer import score_transaction
from .enforcement import is_flagged, store_transaction

_DEMO_ACCOUNTS = [
    "ravi.kumar@okhdfc",
    "priya.sharma@ybl",
    "amit.patel@okicici",
    "sneha.reddy@paytm",
    "vikram.singh@ybl",
    "ananya.iyer@okhdfc",
    "rohit.verma@paytm",
    "kavya.nair@okaxis",
    "arjun.mehta@ybl",
    "divya.joshi@okhdfc",
]

_MULE_ACCOUNTS = ["mule.vendor@paytm", "quick.cash@axis", "cashflow@ybl"]

_MERCHANTS = ["BigBazaar", "Swiggy", "Amazon.in", "Flipkart", "JioMart", "Zomato", "Myntra", "DMart", "Zepto", "Reliance Digital"]

_DEVICES = ["SM-G998B", "iPhone14,2", "Pixel-7", "SM-A525F", "Redmi-K50i", "Xiaomi-12", "Vivo-Y21", "OPPO-F21", "OnePlus-10", "MI-11X"]

_LOCATIONS = ["Mumbai, MH", "Delhi, DL", "Bengaluru, KA", "Pune, MH", "Hyderabad, TS", "Chennai, TN", "Kolkata, WB", "Jaipur, RJ", "Lucknow, UP", "Ahmedabad, GJ"]

_CHANNELS = ["UPI", "IMPS", "CARD", "UPI", "UPI", "UPI"]

_running = False
_task: Optional[asyncio.Task] = None
_started_at: Optional[str] = None
_counts = {"sent": 0, "blocked": 0, "review": 0}


def _rng():
    return random.Random()


def _gen_txn() -> dict:
    r = random.Random()
    scenario = r.random()

    if scenario < 0.07:
        src = r.choice(_MULE_ACCOUNTS)
        amount = r.choice([1.0, 2.5, 50000, 99000, 100000, 45000, 75000])
        channel = "UPI"
        loc = r.choice(_LOCATIONS)
        device = r.choice(_DEVICES)
        hour = r.choice([0, 1, 2, 3, 4, 23])
    else:
        src = r.choice(_DEMO_ACCOUNTS)
        amount = round(r.choice([120.0, 450.0, 899.0, 1500.0, 2500.0, 5200.0, 12000.0, 23000.0, 35000.0]), 2)
        if r.random() < 0.12:
            amount = round(r.uniform(50, 6000), 2)
        channel = r.choice(_CHANNELS)
        loc = r.choice(_LOCATIONS)
        device = r.choice(_DEVICES)
        hour = r.randint(7, 22)

    dest = r.choice([a for a in _DEMO_ACCOUNTS + _MULE_ACCOUNTS if a != src])
    if channel == "UPI" and r.random() < 0.25:
        dest = r.choice(_MULE_ACCOUNTS)

    txn_time = datetime.now(timezone.utc)
    txn_time = txn_time.replace(hour=hour, minute=r.randint(0, 59), second=r.randint(0, 59))

    txn_ref = f"UPI-{int(txn_time.timestamp() * 1000)}-{r.randint(100, 999)}"
    return {
        "txn_ref": txn_ref,
        "source_ref": src,
        "dest_ref": dest,
        "amount": amount,
        "currency": "INR",
        "channel": channel,
        "txn_type": "P2M" if dest in _MERCHANTS else "P2P",
        "txn_time": txn_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "device_id": device,
        "ip_address": f"103.{r.randint(10, 250)}.{r.randint(0, 250)}.{r.randint(1, 250)}",
        "location": loc,
        "merchant": r.choice(_MERCHANTS) if r.random() < 0.2 else None,
    }


async def _stream_loop(interval: float = 1.4) -> None:
    global _counts
    burst_remaining = 0
    while _running:
        try:
            if burst_remaining > 0:
                burst_remaining -= 1
                await asyncio.sleep(0.25)
            else:
                await asyncio.sleep(interval * _rng().uniform(0.7, 1.6))
                if _rng().random() < 0.10:
                    burst_remaining = _rng().randint(4, 9)

            tx = _gen_txn()
            flagged = await is_flagged(tx["source_ref"]) or await is_flagged(tx["dest_ref"])
            result = await score_transaction(tx, watchlist_hit=flagged)
            await store_transaction(tx, result)
            _counts["sent"] += 1
            if result.decision == "BLOCK":
                _counts["blocked"] += 1
            elif result.decision == "REVIEW":
                _counts["review"] += 1
        except asyncio.CancelledError:
            break
        except Exception:  # noqa: BLE001
            await asyncio.sleep(2.0)


async def start_simulator(interval: float = 1.4) -> dict:
    global _running, _task, _started_at
    if _running:
        return {"status": "running", "started_at": _started_at}
    _running = True
    _started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _counts.update({"sent": 0, "blocked": 0, "review": 0})
    _task = asyncio.create_task(_stream_loop(interval))
    return {"status": "started", "started_at": _started_at}


async def stop_simulator() -> dict:
    global _running, _task
    _running = False
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    return {"status": "stopped", "counts": _counts}


def simulator_status() -> dict:
    return {
        "running": _running,
        "started_at": _started_at,
        "counts": _counts,
    }