# FFMitra — AI-Based Financial Fraud Detection & Prevention

KAVACH 2023 · PS-26 · Real-time fraud detection, fund-trail network graphs, phishing link analysis, and an LLM+RAG victim-assistant chatbot.

**Stack:** FastAPI (Python) · React 18 + Vite + TypeScript · Tailwind · Supabase (Postgres + Auth + Realtime + pgvector) · XGBoost + IsolationForest + SHAP · Gemini LLM (RAG).

## v2 — Public Victim Portal (Streamlit)

New in v2:
- **Public victim portal — no login needed** (victims are anonymous by design; analysts sign in to the command center).
- **Voice victim assistant** — victims record their complaint; Gemini transcribes it and Mitra answers with the same RAG guidance (endpoint `/api/chat/voice` + mic button in React chat).

```bash
pip install -r streamlit_app/requirements.txt
cp streamlit_app/.streamlit/secrets.example.toml streamlit_app/.streamlit/secrets.toml  # fill keys
streamlit run streamlit_app/app.py   # http://localhost:8501
```

**Deploy to Streamlit Community Cloud (free):**
1. Push this repo to GitHub.
2. [share.streamlit.io](https://share.streamlit.io) → New app → pick the repo → main file `streamlit_app/app.py` → Deploy.
3. App settings → Secrets → paste the keys from `.streamlit/secrets.example.toml`.

The app embeds the FFMitra engine (ML scorer, RAG, Supabase, Gemini) directly — no separate backend needed on the cloud.

## Architecture

```
Frontend (React/Vite) ──> /api ──> FastAPI backend
                                   ├── ML scorer (XGBoost + IsolationForest + 14 rules, SHAP explanations)
                                   ├── Fund-trail graph (networkx: concentrator / splitter / cycle / mule)
                                   ├── Phishing link analyzer (heuristics + Gemini fallback)
                                   ├── Realtime simulator (SSE) → live alerts
                                   └── Chatbot (Gemini + pgvector RAG over 43 RBI/PSU FAQs)
Supabase (hosted): Postgres tables, Auth (analyst login), Realtime broadcast, pgvector embeddings
```

## Quick Start

### 1. Prerequisites
- Python 3.12+, Node 20+, or Docker + Docker Compose
- A free Supabase project + Gemini API key

### 2. Configure
```bash
cp .env.example .env
# fill in SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY,
# SUPABASE_DB_URL (postgresql://postgres.<ref>:[DB_PASSWORD]@...pooler.supabase.com:6543/postgres),
# GEMINI_API_KEY
```

### 3. One-time: create schema + seed
```bash
python backend/scripts/run_migrations.py   # applies supabase/migrations/0001_init.sql
python backend/scripts/seed_faq.py         # 43 FAQ docs → pgvector (768-dim Gemini embeddings)
python backend/scripts/seed_data.py        # synthetic accounts + transactions
python backend/scripts/admin_user.py       # creates admin@ffmitra.local / Analyst@2026
```

### 4. Run locally
```bash
cd backend && .venv/Scripts/python -m uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev   # http://localhost:5173
```

### 5. Or run with Docker
```bash
docker compose up --build   # frontend :80, backend :8000
```

## Demo Script (5 minutes)

1. **Login** — `admin@ffmitra.local` / `Analyst@2026` (create via `admin_user.py`).
2. **Dashboard** — live feed, KPIs, fraud risk gauge.
3. **Live simulation** — Admin → Start Simulator. Watch streaming transactions and auto-flagging in real time.
4. **Flag an account** — Flag `mule.vendor@paytm`; watch the realtime auto-block alert fire on the next incoming transaction to it.
5. **Fund trail** — Investigate → trace the flagged account; the graph shows flow in/out with mule/concentrator markers.
6. **Link Analyzer** — paste a suspicious URL (e.g. `http://hdfc-secure-login.xyz/verify`) → risk score + recommendation.
7. **Victim Assistant** — chat as a victim; ask "I got a call from my bank asking for my OTP" → category, urgency, RBI guidance.
8. **Reports** — charts by category/channel; case management in **Cases**.

## API Surface (all `/api/*` except `/healthz` require Bearer JWT from Supabase Auth)

- `GET /healthz`
- `POST /api/transactions/score` · `POST /api/transactions/ingest` · `GET /api/transactions/:ref` · `GET /api/transactions`
- `GET /api/investigate/account/:ref` · `GET /api/investigate/txn/:ref`
- `GET|POST /api/flagged` · `POST /api/flagged/flag` · `POST /api/flagged/unflag` · `GET /api/flagged/:ref/activity`
- `GET|POST /api/cases` · `GET|PATCH /api/cases/:id` · `GET /api/cases/:id/notes`
- `POST /api/links/analyze`
- `POST /api/chat/message` · `POST /api/chat/session` · `GET /api/chat/categories`
- `GET /api/dashboard/live` · `GET /api/dashboard/stats` · `GET /api/dashboard/live`
- `GET|POST /api/admin/simulator` · `GET /api/admin/settings` · `POST /api/simulator/start|stop` · `GET /api/simulator/status`

> Realtime UI updates flow through **Supabase Realtime** (tables `transactions`, `alerts`, `flagged_accounts` published via `0001_init.sql`), not SSE.

## Model Performance

XGBoost trained on 213,785 synthetic+public card transactions — accuracy 0.9941, recall 0.9632, PR-AUC 0.9702, ROC-AUC 0.9957. Top drivers: amount, new_location, new_device, midnight_txn, 1h sum amount.

## Notes
- `text-embedding-004` may 404 on some keys → embeddings auto-fallback to `gemini-embedding-2` (dim 768, matches `faq_docs.embedding vector(768)`).
- Realtime broadcast requires the tables' realtime publication (applied by `0001_init.sql` via guarded DO blocks).
- **Security:** rotate the Supabase secret key before any public deployment.
- Data dirs (`data/models`, `data/datasets`, `data/artifacts`) are gitignored; run `backend/scripts/train.py` to regenerate models if lost.

## Tests
```bash
cd backend && .venv/Scripts/python -m pytest tests -q
```
