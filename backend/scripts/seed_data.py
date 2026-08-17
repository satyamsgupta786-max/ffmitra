from __future__ import annotations

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

ACCOUNTS: list[dict] = [
    {"account_ref": "ravi.kumar@okhdfc", "account_type": "UPI", "holder_name": "Ravi Kumar", "bank": "HDFC"},
    {"account_ref": "priya.sharma@ybl", "account_type": "UPI", "holder_name": "Priya Sharma", "bank": "ICICI"},
    {"account_ref": "amit.patel@okicici", "account_type": "UPI", "holder_name": "Amit Patel", "bank": "ICICI"},
    {"account_ref": "sneha.reddy@oksbi", "account_type": "UPI", "holder_name": "Sneha Reddy", "bank": "SBI"},
    {"account_ref": "vikram.singh@ybl", "account_type": "UPI", "holder_name": "Vikram Singh", "bank": "Axis"},
    {"account_ref": "ananya.iyer@okhdfc", "account_type": "UPI", "holder_name": "Ananya Iyer", "bank": "HDFC"},
    {"account_ref": "rohit.verma@okpnb", "account_type": "UPI", "holder_name": "Rohit Verma", "bank": "PNB"},
    {"account_ref": "kavya.nair@okaxis", "account_type": "UPI", "holder_name": "Kavya Nair", "bank": "Axis"},
    {"account_ref": "50100234567890", "account_type": "SAVINGS", "holder_name": "Arjun Mehta", "bank": "Kotak"},
    {"account_ref": "912345678901234", "account_type": "SAVINGS", "holder_name": "Divya Joshi", "bank": "Yes Bank"},
]

FLAGGED_ACCOUNTS: list[dict] = [
    {"account_ref": "mule.vendor@paytm", "reason": "Suspected mule account — high velocity incoming", "severity": "HIGH", "source": "SUSPECT_IMPORT"},
    {"account_ref": "quick.cash@axis", "reason": "Suspected mule account — high velocity outgoing", "severity": "HIGH", "source": "SUSPECT_IMPORT"},
    {"account_ref": "9988776655@ybl", "reason": "Phone number reported in multiple fraud complaints", "severity": "HIGH", "source": "SUSPECT_IMPORT"},
]

ALERTS: list[dict] = [
    {"txn_ref": "UPI-000000000015", "alert_type": "AUTO_BLOCK", "severity": "HIGH", "title": "Automated block on round-amount transfer", "description": "99,000 INR round transfer blocked by rule engine", "account_ref": "mule.vendor@paytm", "acknowledged": False},
    {"txn_ref": "UPI-000000000024", "alert_type": "FRAUD_SCORE", "severity": "MEDIUM", "title": "Fraud score above review threshold", "description": "ML fraud score 0.62 exceeded review threshold 0.6", "account_ref": "quick.cash@axis", "acknowledged": False},
    {"txn_ref": "UPI-000000000036", "alert_type": "WATCHLIST_HIT", "severity": "HIGH", "title": "Destination matched watchlist", "description": "Recipient account is on the flagged accounts watchlist", "account_ref": "quick.cash@axis", "acknowledged": False},
    {"txn_ref": "UPI-000000000048", "alert_type": "ANOMALY", "severity": "LOW", "title": "Unusual-hour transaction detected", "description": "Transaction executed in the early hours outside usual activity window", "account_ref": "mule.vendor@paytm", "acknowledged": False},
]

CASES: list[dict] = [
    {"case_no": "FMC-2026-0001", "title": "UPI fraud — funds transferred to mule account", "category": "Payment / Transaction Fraud", "status": "OPEN", "summary": "Victim was lured via a phishing SMS and transferred 99,000 INR to a mule account. Transaction UPI-000000000015 flagged by AUTO_BLOCK.", "victim_name": "Ravi Kumar", "victim_contact": "+91-9876501234", "source": "MANUAL", "created_by": "analyst@ffmitra.local"},
    {"case_no": "FMC-2026-0002", "title": "Phishing link in fake bank email", "category": "Phishing & Social Engineering", "status": "IN_PROGRESS", "summary": "", "victim_name": "", "victim_contact": "", "source": "MANUAL", "created_by": "analyst@ffmitra.local"},
    {"case_no": "FMC-2026-0003", "title": "Investment scam payout pattern", "category": "Investment & Misleading Payments", "status": "OPEN", "summary": "", "victim_name": "", "victim_contact": "", "source": "MANUAL", "created_by": "analyst@ffmitra.local"},
]

CASE_NOTE = {"note": "Initial triage complete — alerted accounts pulled, transaction trail UPI-000000000015 captured, awaiting bank statement.", "author": "analyst@ffmitra.local"}


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def rest_url() -> str:
    return f"{os.environ['SUPABASE_URL'].rstrip('/')}/rest/v1"


def headers(prefer: str = "return=minimal") -> dict[str, str]:
    secret = os.environ["SUPABASE_SECRET_KEY"]
    return {
        "apikey": secret,
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def build_transactions() -> list[dict]:
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    refs = [a["account_ref"] for a in ACCOUNTS]
    flagged_refs = [f["account_ref"] for f in FLAGGED_ACCOUNTS]
    channels = ["UPI", "UPI", "UPI", "UPI", "IMPS", "IMPS", "CARD", "RTGS", "NEFT"]
    txn_types = ["P2P", "P2P", "P2P", "P2P", "P2M", "P2M", "ATM"]
    merchants = ["Amazon Pay", "Swiggy", "DMart", "IRCTC", "Flipkart", "Zomato", "JioMart", "BigBasket"]
    cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Jaipur", "Kolkata"]
    rows: list[dict] = []
    last_time = now
    for i in range(1, 121):
        source, dest = rng.sample(refs, 2)
        if i % 15 == 0:
            amount = 99000.00
            dest = rng.choice(flagged_refs)
        elif i % 12 == 0:
            amount = 50000.00
            dest = rng.choice(flagged_refs)
        elif i % 11 == 0:
            amount = float(rng.choice([1.00, 2.50, 5.00]))
        else:
            amount = round(rng.uniform(50.0, 95000.0), 2)
        if i % 7 == 0:
            txn_time = last_time + timedelta(minutes=rng.randint(1, 9))
        else:
            txn_time = now - timedelta(hours=rng.uniform(0.0, 72.0))
        last_time = txn_time
        if txn_time > now:
            txn_time = now - timedelta(minutes=1)
        if i % 9 == 0:
            txn_time = txn_time.replace(hour=3, minute=rng.randint(0, 59), second=0, microsecond=0)
        channel = rng.choice(channels)
        txn_type = rng.choice(txn_types)
        rows.append({
            "txn_ref": f"UPI-{i:012d}",
            "source_ref": source,
            "dest_ref": dest,
            "amount": amount,
            "currency": "INR",
            "channel": channel,
            "txn_type": txn_type,
            "txn_time": txn_time.isoformat(),
            "device_id": f"dev-{rng.randint(100000, 999999)}",
            "ip_address": f"103.{rng.randint(1, 255)}.{rng.randint(1, 255)}.{rng.randint(1, 255)}",
            "location": rng.choice(cities),
            "merchant": rng.choice(merchants) if txn_type == "P2M" else None,
        })
    return rows


def score_rows(rows: list[dict]) -> list[dict]:
    """Score each seed transaction with the real ML + rule engine so seeded
    decisions match live behaviour (BLOCK on mule destinations, etc.)."""
    from app.ml.scorer import score_transaction

    async def run() -> list[dict]:
        out = []
        for row in rows:
            watchlist = row["dest_ref"] in [f["account_ref"] for f in FLAGGED_ACCOUNTS]
            result = await score_transaction(row, watchlist_hit=watchlist)
            out.append(
                {
                    **row,
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
            )
        return out

    return asyncio.run(run())


def upsert(client: httpx.Client, table: str, rows: list[dict], conflict_col: str) -> None:
    resp = client.post(
        f"{rest_url()}/{table}",
        params={"on_conflict": conflict_col},
        headers=headers("return=minimal,resolution=merge-duplicates"),
        json=rows,
    )
    resp.raise_for_status()


def table_empty(client: httpx.Client, table: str) -> bool:
    resp = client.get(f"{rest_url()}/{table}", params={"select": "id", "limit": 1}, headers=headers())
    resp.raise_for_status()
    return len(resp.json()) == 0


def seed() -> dict[str, int]:
    counts: dict[str, int] = {}
    with httpx.Client(timeout=60.0) as client:
        upsert(client, "accounts", ACCOUNTS, "account_ref")
        counts["accounts"] = len(ACCOUNTS)

        transactions = score_rows(build_transactions())
        upsert(client, "transactions", transactions, "txn_ref")
        counts["transactions"] = len(transactions)

        upsert(client, "flagged_accounts", FLAGGED_ACCOUNTS, "account_ref")
        counts["flagged_accounts"] = len(FLAGGED_ACCOUNTS)

        if table_empty(client, "alerts"):
            resp = client.post(f"{rest_url()}/alerts", headers=headers(), json=ALERTS)
            resp.raise_for_status()
            counts["alerts"] = len(ALERTS)
        else:
            counts["alerts"] = 0

        case_resp = client.post(
            f"{rest_url()}/cases",
            params={"on_conflict": "case_no"},
            headers=headers("return=representation,resolution=merge-duplicates"),
            json=CASES,
        )
        case_resp.raise_for_status()
        counts["cases"] = len(CASES)

        if table_empty(client, "case_notes"):
            case_rows = case_resp.json()
            target = next((c for c in case_rows if c.get("case_no") == "FMC-2026-0001"), None)
            if target:
                note = {"case_id": target["id"], **CASE_NOTE}
                note_resp = client.post(f"{rest_url()}/case_notes", headers=headers(), json=note)
                note_resp.raise_for_status()
                counts["case_notes"] = 1
            else:
                counts["case_notes"] = 0
        else:
            counts["case_notes"] = 0
    return counts


def main() -> int:
    load_env()
    if not (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SECRET_KEY")):
        print("SUPABASE_URL and SUPABASE_SECRET_KEY must be set", file=sys.stderr)
        return 1
    try:
        counts = seed()
    except httpx.HTTPError as exc:
        print(f"Seeding failed: {exc}", file=sys.stderr)
        return 1
    print("Seeded FFMitra demo dataset:")
    for table, count in counts.items():
        print(f"  {table}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())