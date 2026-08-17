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
    page_icon="⌬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CYBER_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');

  .stApp {
    background:
      radial-gradient(ellipse at 15% 0%, rgba(0, 255, 156, 0.07), transparent 55%),
      radial-gradient(ellipse at 85% 100%, rgba(56, 189, 248, 0.06), transparent 55%),
      #0a0e14;
  }

  h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; letter-spacing: 0.5px; }

  .cyber-banner {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 3px;
    color: #00ff9c;
    background: linear-gradient(90deg, rgba(0,255,156,0.12), rgba(0,255,156,0.02));
    border: 1px solid rgba(0,255,156,0.35);
    border-left: 4px solid #00ff9c;
    border-radius: 6px;
    padding: 10px 16px;
    margin-bottom: 14px;
    box-shadow: 0 0 18px rgba(0,255,156,0.12);
  }
  .cyber-tag { color: #56d4ff; font-weight: 700; }
  .cyber-dim  { color: #64748b; font-size: 0.8rem; letter-spacing: 2px; }

  [data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid rgba(0, 255, 156, 0.22);
    border-radius: 10px;
    padding: 14px 12px;
    box-shadow: 0 0 14px rgba(0, 255, 156, 0.07);
  }
  [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    color: #00ff9c !important;
  }

  .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid rgba(0, 255, 156, 0.3); }
  .stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; }
  .stTabs [aria-selected="true"] { color: #00ff9c !important; }

  .stButton button, .stDownloadButton button {
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid rgba(0, 255, 156, 0.4) !important;
    border-radius: 6px !important;
    transition: box-shadow 0.2s ease;
  }
  .stButton button:hover, .stDownloadButton button:hover {
    box-shadow: 0 0 16px rgba(0, 255, 156, 0.45) !important;
  }

  [data-testid="stSidebar"] {
    background: #0c1118;
    border-right: 1px solid rgba(0, 255, 156, 0.15);
  }

  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    font-family: 'Orbitron', sans-serif !important;
  }

  .cyber-badge { font-family: 'JetBrains Mono', monospace; font-weight: 700; letter-spacing: 1px; }

  /* subtle scanlines */
  .stApp::after {
    content: "";
    position: fixed; inset: 0; pointer-events: none; z-index: 9999; opacity: 0.5;
    background: repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0 1px, transparent 1px 3px);
  }

  .cyber-alert {
    font-family: 'JetBrains Mono', monospace;
    color: #ff4b4b;
    animation: cyberpulse 1.6s infinite;
  }
  @keyframes cyberpulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }

  .cyber-logo { display: flex; align-items: center; gap: 10px; margin: 2px 0 10px; }
  .logo-hex { animation: hexglow 2.4s ease-in-out infinite; }
  @keyframes hexglow {
    0%, 100% { filter: drop-shadow(0 0 2px rgba(0, 255, 156, 0.4)); }
    50% { filter: drop-shadow(0 0 10px rgba(0, 255, 156, 0.95)); }
  }
  .logo-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    letter-spacing: 2px;
    color: #00ff9c;
    font-size: 1.05rem;
    line-height: 1.1;
  }
  .logo-cursor { animation: blink 1s step-end infinite; color: #56d4ff; }
  @keyframes blink { 50% { opacity: 0; } }
</style>
"""
st.markdown(CYBER_CSS, unsafe_allow_html=True)


def cyber_logo():
    st.markdown(
        '<div class="cyber-logo">'
        '<svg viewBox="0 0 64 64" width="50" height="50">'
        '<defs><linearGradient id="fflg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="#00ff9c"/><stop offset="100%" stop-color="#56d4ff"/>'
        '</linearGradient></defs>'
        '<polygon class="logo-hex" points="32,4 57,18 57,46 32,60 7,46 7,18" fill="none" stroke="url(#fflg)" stroke-width="3"/>'
        '<polygon points="32,9 52.5,20.5 52.5,43.5 32,55 11.5,43.5 11.5,20.5" fill="rgba(0,255,156,0.06)" stroke="rgba(0,255,156,0.35)" stroke-width="1"/>'
        '<text x="32" y="41" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="24" font-weight="700" fill="#00ff9c">FF</text>'
        '</svg>'
        '<div><div class="logo-title">FFMITRA<span class="logo-cursor">▮</span></div>'
        '<div class="cyber-dim" style="letter-spacing:2px;font-size:0.65rem">AI FRAUD SHIELD</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def cyber_banner(text: str, tag: str = "SECURE GRID"):
    st.markdown(
        f'<div class="cyber-banner">⌬ {text} <span class="cyber-tag">// {tag}</span>'
        f'<div class="cyber-dim">FRAUD DEFENSE · RBI GUIDANCE · HELPLINE 1930</div></div>',
        unsafe_allow_html=True,
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
    """Compact Indian-currency formatting: 1.2K / 3.4M / 5.6Cr."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "₹0"
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:.2f}Cr"
    if abs(x) >= 1e6:
        return f"₹{x / 1e6:.2f}M"
    if abs(x) >= 1e3:
        return f"₹{x / 1e3:.1f}K"
    return f"₹{x:,.0f}"


def fmt_time(ts):
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime(
            "%d %b %H:%M"
        )
    except Exception:
        return str(ts)[:16]


def decision_badge(d):
    d = (d or "APPROVE").upper()
    color = {"BLOCK": "#ff4b4b", "REVIEW": "#f2a33c", "APPROVE": "#00ff9c"}.get(d, "#c8d3e0")
    return f'<span class="cyber-badge" style="color:{color}">■ {d}</span>'


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


def _cell(v):
    if isinstance(v, (list, dict)):
        return "; ".join(str(x) for x in v)
    return "" if v is None else str(v)


def csv_download(rows: list[dict], fields: list[str]) -> str:
    import csv

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(fields)
    for r in rows:
        w.writerow([_cell(r.get(f)) for f in fields])
    return buf.getvalue()


def admin_create_user(email: str, password: str) -> tuple[bool, str]:
    """Create an analyst via the Supabase admin API (requires secret key)."""
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not (s.supabase_url and s.supabase_secret_key):
        return False, "Supabase URL / SECRET_KEY not configured."
    headers = {"apikey": s.supabase_secret_key, "Authorization": f"Bearer {s.supabase_secret_key}"}
    try:
        resp = httpx.post(
            f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users",
            headers=headers,
            json={"email": email, "password": password, "email_confirm": True},
            timeout=30.0,
        )
    except Exception as exc:
        return False, f"Network error: {exc}"
    if resp.status_code in (200, 201):
        return True, "ok"
    try:
        detail = resp.json()
    except Exception:
        detail = {}
    if resp.status_code == 422 and "already" in str(detail).lower():
        return False, "A user with this email already exists."
    if resp.status_code == 429:
        return False, "Supabase rate limit hit (HTTP 429) — wait a few minutes, then retry."
    return False, f"Admin API HTTP {resp.status_code}: {str(detail)[:200]}"


def admin_list_users() -> tuple[list[dict], str | None]:
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not (s.supabase_url and s.supabase_secret_key):
        return [], "Supabase URL / SECRET_KEY not configured."
    headers = {"apikey": s.supabase_secret_key, "Authorization": f"Bearer {s.supabase_secret_key}"}
    try:
        resp = httpx.get(
            f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users?per_page=100",
            headers=headers,
            timeout=30.0,
        )
    except Exception as exc:
        return [], f"Network error: {exc}"
    if resp.status_code != 200:
        return [], f"Admin API HTTP {resp.status_code}: {resp.text[:200]}"
    return resp.json().get("users", []), None


def update_self_password(new_pw: str, access_token: str) -> tuple[bool, str]:
    """Change the signed-in analyst's password using their session token."""
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not s.supabase_url:
        return False, "Supabase URL not configured."
    headers = {
        "apikey": s.supabase_publishable_key or s.supabase_secret_key,
        "Authorization": f"Bearer {access_token}",
    }
    try:
        resp = httpx.put(
            f"{s.supabase_url.rstrip('/')}/auth/v1/user",
            headers=headers,
            json={"password": new_pw},
            timeout=30.0,
        )
    except Exception as exc:
        return False, f"Network error: {exc}"
    if resp.status_code == 200:
        return True, "ok"
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"


def admin_reset_password(email: str, new_pw: str) -> tuple[bool, str]:
    """Reset another analyst's password via the Supabase admin API."""
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not (s.supabase_url and s.supabase_secret_key):
        return False, "Supabase URL / SECRET_KEY not configured."
    users, _ = admin_list_users()
    target = next((u for u in users if u.get("email") == email), None)
    if not target:
        return False, "User not found."
    headers = {"apikey": s.supabase_secret_key, "Authorization": f"Bearer {s.supabase_secret_key}"}
    try:
        resp = httpx.put(
            f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users/{target['id']}",
            headers=headers,
            json={"password": new_pw},
            timeout=30.0,
        )
    except Exception as exc:
        return False, f"Network error: {exc}"
    if resp.status_code in (200, 201, 204):
        return True, "ok"
    return False, f"Admin API HTTP {resp.status_code}: {resp.text[:200]}"


def admin_delete_user(email: str, users: list[dict]) -> tuple[bool, str]:
    """Permanently remove an analyst via the Supabase admin API."""
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not (s.supabase_url and s.supabase_secret_key):
        return False, "Supabase URL / SECRET_KEY not configured."
    target = next((u for u in users if u.get("email") == email), None)
    if not target:
        return False, "User not found."
    headers = {"apikey": s.supabase_secret_key, "Authorization": f"Bearer {s.supabase_secret_key}"}
    try:
        resp = httpx.delete(
            f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users/{target['id']}",
            headers=headers,
            timeout=30.0,
        )
    except Exception as exc:
        return False, f"Network error: {exc}"
    if resp.status_code in (200, 204):
        return True, "ok"
    return False, f"Admin API HTTP {resp.status_code}: {resp.text[:200]}"


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
    cyber_banner("FFMITRA MITRA", "VICTIM ASSISTANT · ANONYMOUS")
    st.title("⌬ FFMitra Mitra — Fraud Victim Assistant")
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
    cyber_banner("FFMITRA COMMAND CENTER", "ANALYST ACCESS ONLY")
    st.title("⌬ FFMitra Command Center")
    st.caption(f"Signed in as **{AUTH['email']}**")

    tab_dash, tab_txns, tab_flag, tab_trail, tab_links, tab_admin = st.tabs(
        ["Dashboard", "Transactions", "Flag Accounts", "Fund Trail", "Link Analyzer", "Admin"]
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
                        f"{fmt_time(t.get('txn_time'))}",
                        unsafe_allow_html=True,
                    )

        live_dashboard()

        dl_recent = run(db.select("transactions", order="txn_time.desc", limit=200))
        dl_blocked = [t for t in dl_recent if (t.get("risk_decision") or "APPROVE").upper() == "BLOCK"]
        dl_review = [t for t in dl_recent if (t.get("risk_decision") or "APPROVE").upper() == "REVIEW"]
        dl_fields = ["txn_ref", "txn_time", "source_ref", "dest_ref", "amount", "risk_score", "risk_decision", "risk_reasons"]
        d1, d2, d3 = st.columns(3)
        d1.download_button(
            "⬇️ Summary report (CSV)",
            data=csv_download(
                [{"transactions": len(dl_recent), "volume": sum(float(t.get("amount") or 0) for t in dl_recent), "blocked": len(dl_blocked), "review": len(dl_review)}],
                ["transactions", "volume", "blocked", "review"],
            ),
            file_name="ffmitra-summary.csv",
            mime="text/csv",
            key="dl_summary",
        )
        d2.download_button(
            "⬇️ Blocked transactions (CSV)",
            data=csv_download(dl_blocked, dl_fields),
            file_name="ffmitra-blocked.csv",
            mime="text/csv",
            key="dl_blocked",
        )
        d3.download_button(
            "⬇️ Review queue (CSV)",
            data=csv_download(dl_review, dl_fields),
            file_name="ffmitra-review-queue.csv",
            mime="text/csv",
            key="dl_review",
        )

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
            st.download_button(
                "⬇️ Download all transactions (CSV)",
                data=csv_download(
                    rows,
                    ["txn_ref", "txn_time", "source_ref", "dest_ref", "amount", "risk_score", "risk_decision", "risk_reasons"],
                ),
                file_name="ffmitra-transactions.csv",
                mime="text/csv",
                key="dl_txns",
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
        flagged_rows = run(db.select("flagged_accounts", {"active": "true"}, limit=100))
        for f in flagged_rows:
            st.markdown(f"🚫 `{f.get('account_ref')}` — {f.get('reason')} · {fmt_time(f.get('created_at'))}")
        st.download_button(
            "⬇️ Download watchlist (CSV)",
            data=csv_download(flagged_rows, ["account_ref", "reason", "severity", "source", "created_at"]),
            file_name="ffmitra-flagged-accounts.csv",
            mime="text/csv",
            key="dl_flag",
        )

    with tab_trail:
        from app.graph.fundtrail import build_fund_trail

        seed = st.text_input("Account to trace", value="mule.vendor@paytm", key="trail_acc")
        depth = st.slider("Depth", 1, 3, 2)
        if st.button("Trace", type="primary") and seed.strip():
            with st.spinner("Building fund trail…"):
                result = run(build_fund_trail(seed.strip(), depth=depth))
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

    with tab_admin:
        st.markdown("#### 👮 Create analyst account")
        st.caption(
            "Anyone can be made an analyst — but you must confirm with the "
            "**admin password** (the password of the account you signed in with). "
            "New analysts sign in at the sidebar with the temporary password you set."
        )
        new_email = st.text_input("New analyst email", key="admin_new_email")
        new_pw = st.text_input("Temporary password", type="password", key="admin_new_pw")
        confirm_pw = st.text_input("Your admin password (authorization)", type="password", key="admin_confirm_pw")
        if st.button("Create analyst", type="primary"):
            if not new_email.strip() or not new_pw or not confirm_pw:
                st.warning("Fill in all three fields.")
            else:
                auth2, err = login(AUTH["email"], confirm_pw)
                if err:
                    st.error(f"❌ Authorization failed — wrong admin password: {err}")
                else:
                    ok, msg = admin_create_user(new_email.strip(), new_pw)
                    if ok:
                        st.success(f"✅ Analyst **{new_email.strip()}** created — they can sign in with the temporary password.")
                    else:
                        st.error(f"❌ {msg}")
        st.divider()
        st.subheader("Remove analyst")
        deletable_users, err2 = admin_list_users()
        if err2:
            st.error(err2)
        deletable = [u for u in deletable_users if u.get("email") != AUTH["email"]]
        if not deletable_users:
            st.markdown("_No analysts found._")
        elif not deletable:
            st.markdown("_Only your own account exists — you can't remove yourself._")
        else:
            victim_email = st.selectbox(
                "Analyst to remove",
                [u["email"] for u in deletable],
                key="admin_remove_email",
            )
            if victim_email == "admin@ffmitra.local":
                st.warning(
                    "⚠️ This is the **demo analyst** account (`admin@ffmitra.local` / `Analyst@2026`). "
                    "Removing it means the published demo credentials stop working."
                )
            rm_confirm = st.checkbox("I understand this permanently removes the account", key="admin_remove_confirm")
            rm_pw = st.text_input("Your admin password (to remove)", type="password", key="admin_remove_pw")
            if st.button("🗑 Remove analyst", type="secondary"):
                if not rm_confirm or not rm_pw:
                    st.warning("Confirm the checkbox and enter your admin password.")
                else:
                    auth3, err3 = login(AUTH["email"], rm_pw)
                    if err3:
                        st.error(f"❌ Authorization failed — wrong admin password: {err3}")
                    else:
                        ok3, msg3 = admin_delete_user(victim_email, deletable_users)
                        if ok3:
                            st.success(f"🗑 Analyst **{victim_email}** removed.")
                        else:
                            st.error(f"❌ {msg3}")
        st.divider()
        st.subheader("🔑 Change my password")
        cur_pw = st.text_input("Current password", type="password", key="chg_cur_pw")
        new_pw1 = st.text_input("New password", type="password", key="chg_new_pw")
        new_pw2 = st.text_input("Repeat new password", type="password", key="chg_new_pw2")
        if st.button("Update my password", type="secondary"):
            if not cur_pw or not new_pw1 or not new_pw2:
                st.warning("Fill all three fields.")
            elif new_pw1 != new_pw2:
                st.warning("New passwords do not match.")
            else:
                authx, errx = login(AUTH["email"], cur_pw)
                if errx:
                    st.error(f"❌ Wrong current password: {errx}")
                else:
                    okx, msgx = update_self_password(new_pw1, authx["token"])
                    if okx:
                        st.success("✅ Password updated.")
                    else:
                        st.error(f"❌ {msgx}")
        st.divider()
        st.subheader("🔑 Reset analyst password")
        all_users, err4 = admin_list_users()
        if err4:
            st.error(err4)
        elif all_users:
            reset_email = st.selectbox(
                "Analyst to reset",
                [u["email"] for u in all_users],
                key="admin_reset_email",
            )
            reset_pw = st.text_input("New temporary password", type="password", key="admin_reset_pw")
            reset_admin_pw = st.text_input("Your admin password (to reset)", type="password", key="admin_reset_admin_pw")
            if st.button("Reset password", type="secondary"):
                if not reset_pw or not reset_admin_pw:
                    st.warning("Fill both password fields.")
                else:
                    authx2, errx2 = login(AUTH["email"], reset_admin_pw)
                    if errx2:
                        st.error(f"❌ Authorization failed — wrong admin password: {errx2}")
                    else:
                        okx2, msgx2 = admin_reset_password(reset_email, reset_pw)
                        if okx2:
                            st.success(f"✅ Password reset for **{reset_email}**.")
                        else:
                            st.error(f"❌ {msgx2}")
        st.divider()
        st.subheader("🖥️ System health")
        from app.config import get_settings as _gs2

        _s3 = _gs2()
        st.markdown(
            f"- Supabase URL: {'✅ set' if _s3.supabase_url else '❌ missing'}\n"
            f"- Supabase SECRET_KEY: {'✅ set' if _s3.supabase_secret_key else '❌ missing'}\n"
            f"- Gemini key: {'✅ set' if _s3.has_gemini else '❌ missing'}"
        )
        st.divider()
        st.subheader("Current analysts")
        users, err2 = admin_list_users()
        if err2:
            st.error(err2)
        elif not users:
            st.markdown("_No analysts found._")
        else:
            for u in users:
                last = fmt_time(u.get("last_sign_in_at")) if u.get("last_sign_in_at") else "never"
                st.markdown(f"- `{u.get('email')}` · created {fmt_time(u.get('created_at'))} · last seen {last}")
        st.download_button(
            "⬇️ Download analyst list (CSV)",
            data=csv_download(users, ["email", "created_at", "last_sign_in_at"]),
            file_name="ffmitra-analysts.csv",
            mime="text/csv",
            key="dl_analysts",
        )


# ---------------------------------------------------------------------------
# sidebar + routing
# ---------------------------------------------------------------------------

with st.sidebar:
    cyber_logo()

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
    else:
        st.markdown(f"👤 **{AUTH['email']}**")
        if st.button("Sign out", use_container_width=True):
            st.session_state.auth = None
            st.rerun()

    page = st.radio(
        "Navigate",
        ["⌬ Victim Assistant (public)", "🕵️ Command Center (analyst)"],
    )

if page.startswith("⌬"):
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