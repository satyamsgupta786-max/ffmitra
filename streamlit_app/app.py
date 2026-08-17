# FFMitra v2 — public victim portal + analyst command center (Streamlit)
# Reuses the FFMitra engine directly (ML scorer, RAG, Supabase, Gemini).

from __future__ import annotations

import asyncio
import io
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# --- secrets -> env (Streamlit Cloud has no .env; pydantic-settings reads env first) ---
def _flatten_secrets(prefix: str, obj) -> None:
    """Accept flat keys OR a [secrets] section — both work on Streamlit Cloud."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten_secrets(f"{prefix}.{k}" if prefix else k, v)
    else:
        key = prefix.upper().replace(".", "_")
        if isinstance(obj, str) and key in (
            "SUPABASE_URL",
            "SUPABASE_PUBLISHABLE_KEY",
            "SUPABASE_SECRET_KEY",
            "GEMINI_API_KEY",
            "GEMINI_MODEL",
            "GEMINI_EMBEDDING_MODEL",
            "GEMINI_BASE_URL",
        ):
            os.environ.setdefault(key, obj)


try:
    _flatten_secrets("", dict(st.secrets))
except Exception:
    pass

from app.db import get_db
from app.ml.scorer import score_transaction
from app.rag.chat_llm import generate_reply, load_docs, process_voice_message
from app.services.enforcement import flag_account, is_flagged

st.set_page_config(
    page_title="FFMitra — AI Fraud Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def run(coro):
    """Run a coroutine in its own event loop.

    The SupabaseDB client is bound to whichever loop created it, and each
    asyncio.run() spins up a NEW loop — so we force a fresh client per call
    and close it inside its own loop (otherwise: 'Event loop is closed').
    """
    db = get_db()
    db._client = None

    async def _go():
        try:
            return await coro
        finally:
            if db._client is not None and not db._client.is_closed:
                await db._client.aclose()
            db._client = None

    return asyncio.run(_go())


def fmt_inr(v):
    try:
        return f"₹{float(v):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def fmt_time(ts):
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime(
            "%d %b %H:%M"
        )
    except Exception:
        return str(ts)[:16]


def decision_badge(d):
    d = (d or "APPROVE").upper()
    if d == "BLOCK":
        return "🚫 **BLOCK**"
    if d == "REVIEW":
        return "⚠️ **REVIEW**"
    return "✅ APPROVE"


def login(email: str, password: str) -> tuple[dict | None, str | None]:
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not s.supabase_url:
        return None, "Supabase URL is not configured — add secrets in Settings → Secrets."
    try:
        resp = httpx.post(
            f"{s.supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
            headers={
                "apikey": s.supabase_publishable_key or s.supabase_secret_key,
                "Content-Type": "application/json",
            },
            json={"email": email, "password": password},
            timeout=30.0,
        )
        if resp.status_code != 200:
            try:
                detail = resp.json().get("error_description") or resp.json().get("msg")
            except Exception:
                detail = None
            return None, detail or f"Supabase rejected login (HTTP {resp.status_code})"
        data = resp.json()
        return {"token": data["access_token"], "email": data["user"]["email"]}, None
    except Exception as exc:
        return None, f"Network error: {exc}"


# ---------------------------------------------------------------------------
# auth state
# ---------------------------------------------------------------------------

if "auth" not in st.session_state:
    st.session_state.auth = None

AUTH = st.session_state.auth


# ---------------------------------------------------------------------------
# page: victim assistant (public — no login)
# ---------------------------------------------------------------------------

def page_victim():
    st.title("🛡️ FFMitra Mitra — Fraud Victim Assistant")
    st.caption(
        "**No login needed.** You are anonymous. Tell us what happened — in your "
        "own words or with your voice — and Mitra guides you, grounded in RBI / "
        "police guidance (helpline 1930, cybercrime.gov.in)."
    )

    docs, _ = load_docs()

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("💬 Tell Mitra what happened")
        question = st.text_area(
            "Describe the incident",
            placeholder="e.g. I got a call from my bank asking for my OTP and card number. I shared it. What should I do now?",
            height=110,
        )
        voice = st.audio_input("🎙️ …or record your voice note", key="voice_in")
        if voice is not None:
            audio_bytes = voice.getvalue()
            mime = getattr(voice, "type", "audio/wav") or "audio/wav"
            if st.button("Send voice note", type="primary"):
                with st.spinner("Listening to you…"):
                    result = process_voice_message(audio_bytes, mime, [], docs)
                if result.get("transcript"):
                    st.info(f"🎙️ I heard: *“{result['transcript']}”*")
                st.session_state.last_reply = result
        if st.button("Send message", type="primary", disabled=not question.strip()):
            with st.spinner("Thinking…"):
                result = generate_reply(question.strip(), [], docs=docs)
            st.session_state.last_reply = result

        reply = st.session_state.get("last_reply")
        if reply:
            cat = reply.get("category", "General")
            urg = reply.get("urgency", "LOW")
            st.markdown("---")
            st.markdown(
                f"**Category:** `{cat}` &nbsp;·&nbsp; **Urgency:** "
                f"`{urg}` &nbsp;·&nbsp; `{'✨ AI' if reply.get('used_llm') else '⚙️ Guideline'}`"
            )
            st.markdown(reply.get("reply", ""))
            if reply.get("urgency") == "CRITICAL":
                st.error("🚨 **Act fast** — call **1930** now and block the transaction with your bank.")

    with col_b:
        st.subheader("🆘 Emergency steps")
        st.markdown(
            """
- **Dial 1930** (cybercrime helpline) — within 10 minutes of the loss.
- **Call your bank** to freeze/block the account.
- **File a complaint** at [cybercrime.gov.in](https://cybercrime.gov.in) (NCRP).
- Keep **evidence**: UTR/transaction IDs, screenshots, SMS, call logs.
- **Never** share OTP, UPI PIN, or screen access with anyone.
"""
        )
        st.subheader("📋 What is covered")
        st.markdown(
            """
- 💳 Payment / Transaction Fraud
- 📞 Phishing & Social Engineering
- 📈 Investment & Misleading Payments
"""
        )


# ---------------------------------------------------------------------------
# page: analyst command center (login required)
# ---------------------------------------------------------------------------

def page_analyst():
    st.title("🛡️ FFMitra Command Center")
    st.caption(f"Signed in as **{AUTH['email']}**")

    tab_dash, tab_txns, tab_flag, tab_trail, tab_links = st.tabs(
        ["Dashboard", "Transactions", "Flag Accounts", "Fund Trail", "Link Analyzer"]
    )

    db = get_db()

    with tab_dash:
        @st.fragment(run_every=5.0)
        def live_dashboard():
            recent = run(db.select("transactions", order="txn_time.desc", limit=200))
            alerts = run(db.select("alerts", order="created_at.desc", limit=50))
            flagged = run(db.select("flagged_accounts", {"active": "true"}, limit=100))

            from collections import Counter

            decisions = Counter(t.get("risk_decision", "APPROVE") for t in recent)
            total = sum(float(t.get("amount") or 0) for t in recent)

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Transactions", len(recent))
            k2.metric("Volume", fmt_inr(total))
            k3.metric("🚫 Blocked", decisions.get("BLOCK", 0))
            k4.metric("⚠️ Review", decisions.get("REVIEW", 0))
            k5.metric("Flagged accts", len(flagged))

            a1, a2 = st.columns(2)
            with a1:
                st.subheader("Recent alerts")
                for a in alerts[:8]:
                    st.markdown(
                        f"`{a.get('alert_type')}` **{a.get('title')}** — "
                        f"{a.get('account_ref') or a.get('txn_ref')} · {fmt_time(a.get('created_at'))}"
                    )
            with a2:
                st.subheader("Latest transactions")
                for t in recent[:8]:
                    st.markdown(
                        f"{decision_badge(t.get('risk_decision'))} {t.get('txn_ref')} · "
                        f"{fmt_inr(t.get('amount'))} · {t.get('source_ref')} → {t.get('dest_ref')} · "
                        f"{fmt_time(t.get('txn_time'))}"
                    )

        live_dashboard()

    with tab_txns:
        q = st.text_input("Search txn ref / account", key="txn_q")
        if q.strip():
            rows = run(db.select("transactions", {"source_ref": q.strip()}, limit=50))
            if not rows:
                rows = run(db.select("transactions", {"dest_ref": q.strip()}, limit=50))
            if not rows:
                rows = run(db.select("transactions", {"txn_ref": q.strip()}, limit=50))
        else:
            rows = run(db.select("transactions", order="txn_time.desc", limit=100))
        if rows:
            st.dataframe(
                [
                    {
                        "Txn": r.get("txn_ref"),
                        "Time": fmt_time(r.get("txn_time")),
                        "From": r.get("source_ref"),
                        "To": r.get("dest_ref"),
                        "Amount": r.get("amount"),
                        "Risk": r.get("risk_score"),
                        "Decision": r.get("risk_decision"),
                        "Reasons": "; ".join((r.get("risk_reasons") or [])[:2]),
                    }
                    for r in rows
                ],
                use_container_width=True,
                height=420,
            )

    with tab_flag:
        st.markdown("Flagging an account adds it to the **watchlist** — the next transaction touching it is **auto-blocked at 99.9**.")
        acc = st.text_input("Account / UPI ID to flag", key="flag_acc")
        reason = st.text_input("Reason", key="flag_reason")
        if st.button("🚫 Flag account", type="primary", disabled=not acc.strip()):
            row = run(flag_account(acc.strip(), reason=reason.strip(), severity="HIGH", source="MANUAL", flagged_by=AUTH["email"]))
            st.success(f"Flagged **{row.get('account_ref')}** — active: {row.get('active')}")
        st.divider()
        st.subheader("Currently flagged")
        for f in run(db.select("flagged_accounts", {"active": "true"}, limit=100)):
            st.markdown(f"🚫 `{f.get('account_ref')}` — {f.get('reason')} · {fmt_time(f.get('created_at'))}")

    with tab_trail:
        from app.graph.fundtrail import build_fund_trail

        seed = st.text_input("Account to trace", value="mule.vendor@paytm", key="trail_acc")
        depth = st.slider("Depth", 1, 3, 2)
        if st.button("Trace", type="primary") and seed.strip():
            with st.spinner("Building fund trail…"):
                result = run(build_fund_trail(seed.strip(), depth=depth, db=db))
            nodes, edges = result["nodes"], result["edges"]
            st.markdown(
                f"**{len(nodes)} accounts · {len(edges)} transfers · "
                f"volume {fmt_inr(result['stats']['volume'])}**"
            )
            for c in result["clusters"]:
                st.markdown(
                    f"`{c['type']}` {c['label']} — {', '.join(c['accounts'][:6])}"
                )
            dot = 'digraph G {\n  rankdir=LR;\n  node [shape=box, style="filled,rounded", fontsize=10];\n'
            for n in nodes:
                color = "#ff4b4b" if n.get("is_seed") else ("#f2a33c" if n.get("risk_level") == "high" else "#9bd1ff")
                dot += f'  "{n["id"]}" [fillcolor="{color}", fontcolor="white"];\n'
            for e in edges:
                dot += f'  "{e["source"]}" -> "{e["target"]}" [label="{fmt_inr(e["amount"])}", fontsize=9, color="#7C5CFF"];\n'
            dot += "}"
            st.graphviz_chart(dot, use_container_width=True)

    with tab_links:
        from app.ml.link_scorer import combine_scores, score_sender, score_url

        url = st.text_input("Suspicious URL", key="link_url")
        sender = st.text_input("Sender (optional)", key="link_sender")
        if st.button("Analyze link", type="primary", disabled=not url.strip()):
            url_score, url_reasons, level = score_url(url.strip())
            sender_score, sender_reasons = score_sender(sender)
            combined, verdict = combine_scores(
                url_score, sender_score, bool(sender and sender.strip())
            )
            st.markdown(
                f"**Risk score:** {round(combined * 100, 1)} / 100 — "
                f"**Level:** `{verdict}`"
            )
            for r in [*url_reasons, *sender_reasons]:
                st.markdown(f"- {r['label']}: {r['detail']}")
            st.markdown(
                "Do not open, share, or enter any details. Report to **1930** immediately."
                if verdict == "HIGH"
                else "Exercise caution — verify through the official app/website only."
            )


# ---------------------------------------------------------------------------
# sidebar + routing
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image(str(REPO_ROOT / "frontend" / "public" / "favicon.svg"), width=56)
    st.markdown("### FFMitra")
    st.caption("AI Financial Fraud Detection & Prevention · v2")

    if AUTH is None:
        st.markdown("#### Analyst login")
        st.caption("Demo: `admin@ffmitra.local` / `Analyst@2026`")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign in", use_container_width=True):
            auth, err = login(email, password)
            if auth:
                st.session_state.auth = auth
                st.rerun()
            else:
                st.error(err or "Invalid credentials")
        if "login_err" in st.session_state and st.session_state.login_err:
            st.error(st.session_state.login_err)

        st.divider()
        st.markdown("##### System status")
        from app.config import get_settings as _gs

        _s = _gs()
        st.markdown(
            f"- Supabase URL: {'✅ set' if _s.supabase_url else '❌ **missing** — add secrets → Settings → Secrets → paste keys → Save → Rerun'}\n"
            f"- Gemini key: {'✅ set' if _s.has_gemini else '❌ missing'}"
        )
    else:
        st.markdown(f"👤 **{AUTH['email']}**")
        if st.button("Sign out", use_container_width=True):
            st.session_state.auth = None
            st.rerun()

    page = st.radio(
        "Navigate",
        ["🛡️ Victim Assistant (public)", "🕵️ Command Center (analyst)"],
    )

if page.startswith("🛡️"):
    page_victim()
else:
    if AUTH is None:
        st.warning("Please sign in to open the Command Center.")
    else:
        page_analyst()

st.markdown("---")
st.caption(
    "FFMitra v2 · KAVACH 2023 PS-26 · Victims are anonymous — no account needed. "
    "Helpline 1930 · cybercrime.gov.in"
)