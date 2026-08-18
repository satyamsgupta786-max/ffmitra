# FFMITRA — AI-BASED FINANCIAL FRAUD DETECTION & PREVENTION PLATFORM

## Presentation Guide & Module Division (6 Members)

> **KAVACH PS-26 · Team Project · Thakur College of Engineering and Technology (TCET)**
> Live app: **https://ffmitra.streamlit.app** · Local React app: `http://localhost:8000` (or `:5173` in dev)
> Demo analyst login: `admin@ffmitra.local` / `Analyst@2026`

---

## 0. OPENING SLIDE (anyone can start — suggested: Team Lead)

### The Problem
- India lost **₹1,453 crore** to digital fraud in 2024 — UPI scams, fake investment apps, "digital arrest" calls, OTP phishing.
- Victims are usually **elderly/less tech-savvy** people who realize too late.
- Banks and apps detect fraud **after** money leaves, and victims have **no friendly 24x7 guide** in between.

### Our Solution — FFMITRA (Fraud-Free Mitra = "friend" in Hindi)
An end-to-end platform with **two audiences**:

| Audience | What they get |
|---|---|
| **Victims / citizens** | AI Mitra chatbot (Hindi-English), voice notes, instant step-by-step rescue (1930 helpline, bank freeze, NCRP complaint), fraud risk assessment of calls/links |
| **Bank analysts / police** | Live dashboard, ML-scored transaction risk, fund-trail graphs, link/URL analyzer, case management, CSV reports, analyst team management |

### Tech Stack (one line each)
- **Backend:** Python FastAPI + REST API (10 routers) on `backend/app/`
- **ML:** scikit-learn/XGBoost ensemble — feature engineering + rules + anomaly scoring (`backend/app/ml/`)
- **AI Assistant:** RAG (retrieval-augmented generation) over a 43-question fraud FAQ corpus, powered by **Qwen (TCET CoE Gateway)** with Gemini fallback (`backend/app/rag/`)
- **Graph:** NetworkX fund-trail traversal + link scoring (`backend/app/graph/`, `backend/app/ml/link_scorer.py`)
- **Database:** Supabase (PostgreSQL + realtime + auth + RLS) — schema in `supabase/migrations/0001_init.sql`
- **Frontend 1 (Analyst web app):** React + TypeScript + Vite + Tailwind cyber theme (`frontend/`)
- **Frontend 2 (Command Center):** Streamlit dashboard with CSV exports + admin panel (`streamlit_app/app.py`)
- **Deployment:** Streamlit Cloud (live) + Docker/Render single-service (`Dockerfile`, `render.yaml`, `docker-compose.yml`)

### Screenshots to take for the opening slide
1. Open **https://ffmitra.streamlit.app** → screenshot the login page.
2. Login with demo credentials → screenshot the **Command Center / Dashboard** (glowing metrics).
3. Open the **React app** locally (`start-host.ps1`) → screenshot **Dashboard** and **Victim Chat** page.

---

## 1. GAURAV — SYSTEM ARCHITECTURE & BACKEND API (FastAPI + Supabase)

### Role
Owns the backend skeleton: how the whole platform connects (FastAPI ↔ Supabase ↔ frontends), plus the core REST endpoints (transactions, dashboard, flagged accounts, cases) and auth.

### What to explain (talking points)
1. **FastAPI app factory** — routers mounted in `backend/app/main.py`; CORS for localhost origins; `/healthz` health endpoint.
2. **Supabase adapter** (`backend/app/db.py`) — thin async client over Supabase REST; the `run()` wrapper that creates a fresh client per event loop (this fixed the famous "event loop is closed" production bug).
3. **Database schema** — 11 tables in `supabase/migrations/0001_init.sql`: `accounts`, `transactions`, `flagged_accounts`, `alerts`, `cases`, `case_notes`, `chat_sessions`, `chat_messages`, `faq_docs`, `settings`; realtime publication for live feed; RLS policies so victims can chat without login.
4. **Auth** (`backend/app/auth.py`) — Supabase auth with publishable/secret key split; admin JWT flow.
5. **API design** — routers in `backend/app/api/`: transactions, dashboard, flagged, cases, investigate, links, chat, admin, simulator. Each returns JSON consumed by BOTH frontends.

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `backend/app/main.py` | Router imports + `include_router` block (line ~39-50) — "one app, ten APIs" |
| `backend/app/db.py` | `run()` / client wrapper + `insert/select/update` methods |
| `backend/app/config.py` | Pydantic Settings reading `.env` |
| `backend/app/api/dashboard.py` | `/api/dashboard/metrics` summary endpoint |
| `backend/app/api/transactions.py` | List + paginate transactions |
| `backend/app/api/cases.py` | Case CRUD + notes |
| `supabase/migrations/0001_init.sql` | Table definitions (whole file) |
| `backend/scripts/seed_data.py` | Seeding 127 transactions + flagged accounts |
| `backend/scripts/run_migrations.py` | Applying SQL to Supabase |
| `backend/app/schemas.py` | Pydantic request/response models |

### Demo (2 minutes)
1. Show `GET /healthz` returning JSON in browser: `http://localhost:8000/healthz`.
2. Open **Supabase dashboard → Table Editor** → show `transactions` (127 rows), `flagged_accounts` (5), `cases`.
3. In the React app → **Transactions** page → show pagination + risk badges (comes from `/api/transactions`).
4. Open **Supabase → Database → Realtime** → show `transactions`/`alerts` live publication (this powers the Live Feed).

### Code to point at for the judge
- `backend/app/db.py` → the `run()` event-loop wrapper (explain *why*: async client bound to a loop → close in same loop).
- `backend/app/main.py` → FastAPI lifespan/startup loads models + RAG corpus at boot (`FFMitra ready in 3.2s | supabase=True models=True`).
- `supabase/migrations/0001_init.sql` → explain RLS: *"anon can insert chat_sessions"* so a victim needs no login.

---

## 2. RITIK — ML FRAUD DETECTION ENGINE (Scoring, Rules, Explainability)

### Role
Owns the heart of detection: the hybrid risk engine that scores every transaction and decides APPROVE / REVIEW / BLOCK.

### What to explain (talking points)
1. **Hybrid scoring** (`backend/app/ml/scorer.py`):
   `final = ml_weight(0.6) * ML probability + anomaly_weight(0.1) * anomaly + rule_weight(0.3) * rule hits`
   → decision thresholds: **review ≥ 0.60, block ≥ 0.90**.
2. **Feature engineering** (`backend/app/ml/features.py`): builds 22 features per transaction — amount z-scores, frequency, velocity (txn count/time window), account history, time-of-day, channel, merchant risk, unusual-hour flags.
3. **Rules engine** (`backend/app/ml/rules.py`): 20+ interpretable rules — e.g., *"large amount to new account", "multiple txns in 1 min", "night-time transfers", "cashback lure patterns"*.
4. **Model training** (`backend/scripts/train.py`): trains on a **synthetic fraud dataset** (500k rows generated in `scripts/generate_synthetic.py`) with scikit-learn + XGBoost; exports to `data/models/`; loads at boot via `ml/loader.py`.
5. **Explainability** (`backend/app/ml/explain.py`): each decision returns **human-readable reasons** ("unusual amount for account", "recipient in flagged list") — shown as badges in UI.

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `backend/app/ml/scorer.py` | `score_transaction()` — weighted formula + thresholds |
| `backend/app/ml/features.py` | Feature functions (velocity, z-score, time patterns) |
| `backend/app/ml/rules.py` | The rule list (nice screenshot of rule constants) |
| `backend/app/ml/explain.py` | Reason generation for each risk factor |
| `backend/app/ml/loader.py` | Model bundle loading + feature list (22) |
| `backend/scripts/train.py` | Pipeline: train → evaluate → export model |
| `backend/scripts/generate_synthetic.py` | Synthetic fraud data generator |
| `backend/app/api/investigate.py` | `/api/investigate/account` — scores + reasons API |
| `backend/notebooks/` (if any) | Training notebook screenshots |

### Demo (2 minutes)
1. React app → **Investigate** page → enter an account (e.g. the flagged ones from `flagged_accounts`) → show score, **HIGH risk badge**, reasons list.
2. **Transactions** page → sort by risk score → show APPROVE / REVIEW / BLOCK badges (DecisionBadge component).
3. **RiskGauge** widget on Dashboard → animate the gauge while explaining thresholds.

### Code to point at for the judge
- `backend/app/ml/scorer.py` → the weighted final score line + threshold constants (`review=0.6, block=0.9`).
- `backend/app/ml/features.py` → one velocity feature function.
- `backend/scripts/generate_synthetic.py` → how "realistic" fraud patterns are injected (amount bursts, new-account spikes).
- `backend/app/api/investigate.py` → how reasons are attached to the API response.

---

## 3. KRISHNA — FUND TRAIL GRAPH & LINK/URL ANALYZER (Network Analytics)

### Role
Owns the money-movement graphs and the fraud link/URL scanner — the tools that connect the dots between accounts and catch scam infrastructure.

### What to explain (talking points)
1. **Fund trail** (`backend/app/graph/fundtrail.py`): NetworkX BFS/DFS traversal of `transactions` — find all accounts reachable from a suspect account (hops, direction), compute **total flow per path**, and return a JSON graph (nodes = accounts, edges = txns) for the frontend to draw.
2. **Graph UI** (`frontend/src/components/FundTrailGraph.tsx`): renders the trail as an interactive force-directed/leveled graph with color-coded HIGH/REVIEW/CLEAN accounts.
3. **Link analyzer** (`backend/app/ml/link_scorer.py`): URL phishing detection **without heavy frameworks** — checks domain age heuristics, suspicious TLDs, "free-rewriter/bit.ly" shorteners, scam keywords ("kyc-update", "refund", "lottery"), HTTPS validity, IP-only hosts; scores 0-100 and returns reasons.
4. **Endpoints** — `backend/app/api/investigate.py` (`/fund-trail`), `backend/app/api/links.py` (re-exported scorer for FastAPI + Streamlit sharing).
5. Works identically in **both frontends** (React LinkAnalyzer.tsx + Streamlit Link Analyzer tab).

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `backend/app/graph/fundtrail.py` | Traversal function + flow aggregation |
| `backend/app/ml/link_scorer.py` | Score function + heuristic list |
| `backend/app/api/investigate.py` | `/fund-trail` endpoint |
| `backend/app/api/links.py` | Router wiring |
| `frontend/src/components/FundTrailGraph.tsx` | Graph rendering code |
| `frontend/src/pages/LinkAnalyzer.tsx` | Analyzer UI code |

### Demo (2 minutes)
1. React app → **Investigate** → pick a source account → **Fund Trail** → screenshot the **graph** (nodes = accounts, edges = ₹ amounts).
2. **Link Analyzer** page → paste `http://bit.ly/free-cashback-kyc-update` → show **score 87/100 + reasons** (red flag list).
3. In Streamlit app (live) → **Fund Trail** tab → paste same account → screenshot graph (graphviz) and CSV download button.

### Code to point at for the judge
- `backend/app/graph/fundtrail.py` → BFS hop traversal + total flow computation.
- `backend/app/ml/link_scorer.py` → the heuristic score function — explain *why no framework* (shared by FastAPI + Streamlit without dependency conflicts).

---

## 4. PRASHANT — AI MITRA CHATBOT (RAG + Qwen CoE Gateway + Voice)

### Role
Owns the victim-facing AI assistant: retrieval-augmented Q&A, the LLM wiring (TCET Qwen gateway + Gemini fallback), voice notes, and the chat page.

### What to explain (talking points)
1. **RAG pipeline** (`backend/app/rag/`):
   - `corpus.py` (905 lines): builds the **43-FAQ fraud corpus** (categories: payment fraud, phishing/social engineering, investment scams) + 768-dim embeddings.
   - `chat_llm.py`: `_rank_docs()` — **embedding similarity first, keyword-overlap fallback** → picks top-4 FAQs per question.
   - `generate_reply()` — system prompt engineering: empathy + Hinglish, urgency-aware ("Act fast —" for CRITICAL), 1930/NCRP reporting steps, ≤220 words.
2. **LLM provider chain** (`backend/app/rag/chat_llm.py`):
   - **Primary: TCET CoE Qwen gateway** (`QWEN_API_KEY`, OpenAI-compatible `/chat/completions`, model `qwen3.6`) — verified live.
   - **Fallback: Gemini** generateContent (retry + 5-min quota cooldown).
   - **Final: deterministic knowledge-base template** — never crashes, always answers.
3. **Classification** — keyword-based category + urgency detection (CRITICAL/MODERATE/LOW).
4. **Voice notes** — mic → `transcribe_audio()` (Gemini inline audio) → same RAG pipeline; React page has animated waveform + REC timer.
5. **Chat storage** — sessions/messages persisted in Supabase with RLS (no login needed); history feeds the LLM context.

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `backend/app/rag/chat_llm.py` | `_rank_docs()`, `generate_reply()`, `_call_qwen()`, `_build_system_prompt()` |
| `backend/app/rag/corpus.py` | Corpus categories + FAQ entries |
| `backend/app/rag/embeddings.py` | Embed model fallback chain + cosine similarity |
| `backend/app/api/chat.py` | `/api/chat/session`, `/message`, `/voice` endpoints |
| `backend/scripts/seed_faq.py` | FAQ seeding |
| `backend/scripts/test_chat.py` | CLI chat tester |
| `frontend/src/pages/VictimChat.tsx` | Chat UI code (animated mic, waveform) |
| `backend/tests/test_chat.py` | Chat tests |

### Demo (2 minutes)
1. React app → **/victim** (or Streamlit **Victim Assistant** page).
2. Type: *"Someone called me saying I have an arrest warrant and asked me to transfer bail money."* → screenshot the **✨ AI reply** with urgency badge + `1930` callout.
3. Repeat with a different question → show it's **not repetitive** (RAG picks different FAQs).
4. Press the **mic** → record → screenshot the **REC waveform + timer**; then show transcript + reply.
5. (Bonus) Show `backend/scripts/test_chat.py` running in a terminal.

### Code to point at for the judge
- `backend/app/rag/chat_llm.py` → `_call_qwen()` — OpenAI-protocol call with Bearer key, 90s timeout, 2 retries; and the **provider fallback chain** in `generate_reply()`.
- `backend/app/rag/chat_llm.py` → `_build_system_prompt()` — show the prompt engineering (Hinglish empathy, urgency rules).
- `backend/app/api/chat.py` → `send_message()` — full flow: save message → classify → rank → generate → persist.

---

## 5. SATYAM — REACT FRONTEND (CYBER UI) & DEPLOYMENT

### Role
Owns the analyst-facing React web app (look, feel, interactions) and the deployment story (local + cloud).

### What to explain (talking points)
1. **App shell** (`frontend/src/App.tsx`) — React Router protected routes (auth guard via Supabase session), 9 pages.
2. **Design system** (`frontend/src/index.css`) — cyber theme: dark ink background, neon cyan/green/red accents, Orbitron/JetBrains Mono fonts, glowing panels, scanline effects, animated hexagon `⌬` logo (`components/Logo.tsx`).
3. **Pages & components**:
   - `Dashboard.tsx` + `KpiCard`, `RiskGauge`, `LiveFeed` (realtime via Supabase channel)
   - `Transactions.tsx` (table + sort + risk bars)
   - `Investigate.tsx` (account deep-dive + fund trail graph)
   - `FlaggedAccounts.tsx`, `Cases.tsx`, `LinkAnalyzer.tsx`, `VictimChat.tsx`, `Reports.tsx` (CSV exports), `Admin.tsx`
   - `Login.tsx` — animated background
4. **Data layer** (`frontend/src/lib/`) — `api.ts` (fetch wrapper with Bearer token), `supabase.ts` (realtime), `utils.ts` (₹ formatting).
5. **Animations** — framer-motion: staggered quick-actions, pulse rings on the mic, REC waveform (framer-motion keyframes), AnimatePresence transitions.
6. **Deployment** — three ways:
   - **Local dev**: `start-dev.ps1` (backend :8000 + vite :5173)
   - **Local hosted build**: `start-host.ps1` → FastAPI serves the built SPA at `http://localhost:8000` (single URL)
   - **Cloud**: `Dockerfile` + `render.yaml` (Render.com free tier, auto-deploy on git push); Streamlit Cloud for the Command Center (`https://ffmitra.streamlit.app`)

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `frontend/src/App.tsx` | Route map (9 protected routes) |
| `frontend/src/index.css` | Theme variables + glow/scanline styles |
| `frontend/src/pages/Dashboard.tsx` | KPI layout + LiveFeed wiring |
| `frontend/src/pages/VictimChat.tsx` | The animated mic + waveform + REC timer |
| `frontend/src/components/RiskGauge.tsx` | SVG gauge |
| `frontend/src/components/Logo.tsx` | Animated hexagon logo |
| `frontend/src/lib/api.ts` | Fetch wrapper |
| `Dockerfile` / `render.yaml` | Single-service deploy config |
| `start-dev.ps1` / `start-host.ps1` | One-click scripts |
| `frontend/vite.config.ts` | `/api` proxy → :8000 |

### Demo (2 minutes)
1. Run `start-host.ps1` → browser opens `http://localhost:8000` → screenshot **login**.
2. Log in (`admin@ffmitra.local` / `Analyst@2026`) → screenshot **Dashboard** with animated KPI cards + Live Feed.
3. Click through pages quickly (Transactions → Investigate → Flagged → Victim Chat) — "smooth and premium".
4. Record a voice note in Victim Chat → show waveform animation.
5. Show `git push` auto-deploying to Render (if deployed) or Streamlit Cloud re-deploy.

### Code to point at for the judge
- `frontend/src/pages/VictimChat.tsx` → the mic button with framer-motion pulse rings + `recSeconds` timer + waveform bars.
- `frontend/src/lib/api.ts` → token attach + error handling.
- `Dockerfile` → multi-stage (node build → python runtime) — explain single-service architecture.
- `backend/app/main.py` (static block at bottom) → SPA fallback that serves index.html for `/victim` etc.

---

## 6. DIVYANSHU — ENFORCEMENT AUTOMATION & STREAMLIT COMMAND CENTER + TESTING

### Role
Owns the analyst command center (Streamlit), automated enforcement workflows, the simulator, and the end-to-end test suite.

### What to explain (talking points)
1. **Streamlit Command Center** (`streamlit_app/app.py`, 810 lines):
   - Dashboard: live KPIs (transactions, blocked, under review), charts, **6 CSV downloads** (summary, blocked, review, all transactions, watchlist, analysts).
   - **Admin tab**: create/remove analyst, change/reset passwords (Supabase admin API), **System health** (Supabase + Qwen gateway + Gemini probes).
   - Cyber theme applied (dark, neon, Orbitron), animated `⌬` logo, compact ₹ formatting (`₹1.2L`, `₹3.4Cr`).
   - Link Analyzer + Fund Trail + Victim Assistant pages (same backend as React app).
2. **Enforcement service** (`backend/app/services/enforcement.py`): auto-action queue — freeze accounts, generate alerts, open cases, notify; integrates with `flagged_accounts`/`alerts`.
3. **Simulator** (`backend/app/services/simulator.py` + `api/simulator.py`): replays synthetic fraud bursts (rapid small txns, new-account spikes) to demonstrate detection live.
4. **Analyst API** (`backend/app/api/admin.py`): user lifecycle via Supabase admin API (avoids JWT-expiry bug — passwords changed server-side).
5. **Testing** — `streamlit_app/test_app.py` runs the FULL E2E via Streamlit's AppTest: victim message → login → command center → link analyzer → fund trail → CSV downloads → create/reset/remove analyst against LIVE Supabase (all green). Backend: `backend/tests/` (26 pytest tests green).

### Files to open & screenshot (for PPT)
| File | What to screenshot |
|---|---|
| `streamlit_app/app.py` | Dashboard metrics + CSV downloads block + Admin tab + System health |
| `backend/app/services/enforcement.py` | Freeze/alert/notify workflow |
| `backend/app/services/simulator.py` | Fraud burst simulation |
| `backend/app/api/admin.py` | Analyst create/remove/reset endpoints |
| `streamlit_app/test_app.py` | The E2E assertions |
| `backend/tests/test_fundtrail.py`, `test_rules.py`, `test_scorer.py` | Unit tests |
| `backend/scripts/admin_user.py` | Bootstrap admin script |

### Demo (2 minutes)
1. Open **https://ffmitra.streamlit.app** → login → screenshot **Command Center dashboard** (metrics + charts).
2. Scroll to **Download buttons** → click "Blocked transactions CSV" → show file opens in Excel.
3. **Admin tab** → create a temp analyst → reset their password → remove them (screenshot each success toast).
4. **System health** → screenshot showing `Supabase ✅ · Qwen gateway ✅ working · Gemini …`.
5. Run in terminal: `python streamlit_app/test_app.py` → show `after victim message exceptions: 0`, `new password login status: 200`, `gone from supabase: True`.

### Code to point at for the judge
- `streamlit_app/app.py` → the `run()` wrapper (event-loop fix) + `csv_download()` helper + `admin_create_user()`.
- `backend/app/services/enforcement.py` → the freeze workflow triggered by BLOCK decisions.
- `streamlit_app/test_app.py` → how AppTest drives the UI and asserts real Supabase state.

---

## 7. END-TO-END LIVE DEMO SCRIPT (10 minutes total)

| Time | What happens | Who |
|---|---|---|
| 0:00-0:30 | Problem + solution intro (2 slides) | Team lead / Satyam |
| 0:30-1:30 | Architecture diagram + Supabase tables | Gaurav |
| 1:30-3:00 | Investigate an account → risk score + reasons + fund trail graph | Ritik + Krishna |
| 3:00-3:30 | Paste scam link into Link Analyzer → high score | Krishna |
| 3:30-5:00 | Victim chat: "digital arrest" call → AI reply → voice note | Prashant |
| 5:00-6:00 | React app tour (dashboard, realtime feed, premium UI) | Satyam |
| 6:00-7:00 | Streamlit Command Center: CSVs, Admin tab, System health | Divyanshu |
| 7:00-8:00 | Simulator: inject fraud burst → watch alerts appear | Divyanshu |
| 8:00-9:00 | Run test suite live (pytest + AppTest E2E) | Divyanshu |
| 9:00-10:00 | Q&A | All |

---

## 8. HOW TO RUN EVERYTHING LOCALLY (for screenshots)

### Option A — Hosted single URL (recommended for screenshots)
```powershell
# in repo root (FFMitra/)
.\start-host.ps1      # builds frontend, starts backend, opens http://localhost:8000
```

### Option B — Dev mode (hot reload)
```powershell
.\start-dev.ps1       # backend :8000 + frontend :5173
```

### Backend alone (if scripts fail)
```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

### Tests
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -q          # 26 unit tests
cd ..
.\.venv\Scripts\python.exe streamlit_app\test_app.py   # full E2E
```

### Live demo credentials
- Analyst: `admin@ffmitra.local` / `Analyst@2026`
- (Extra analysts can be created in Admin tab)

---

## 9. KEY ENDPOINTS CHEAT SHEET (for judges)

| Endpoint | What it does |
|---|---|
| `GET /healthz` | Liveness probe |
| `GET /api/dashboard/metrics` | KPIs for the dashboard |
| `GET /api/transactions?limit=&offset=` | Paginated transactions |
| `GET /api/flagged` | Active flagged accounts |
| `GET /api/investigate/account/{ref}` | Risk score + reasons for an account |
| `GET /api/investigate/fund-trail/{ref}` | Fund trail graph JSON |
| `POST /api/links/analyze` | URL/link phishing score |
| `GET/POST /api/cases` | Case management |
| `POST /api/chat/session` · `POST /api/chat/message` · `POST /api/chat/voice` | AI Mitra endpoints |
| `POST /api/admin/...` | Analyst create/remove/reset |
| `POST /api/simulator/run` | Fraud-burst simulator |

---

## 10. LIKELY JUDGE QUESTIONS & ANSWERS

1. **"How do you decide REVIEW vs BLOCK?"**
   Weighted hybrid score: `0.6·ML + 0.1·anomaly + 0.3·rules`; review ≥ 0.60, block ≥ 0.90. (Ritik)
2. **"What if the LLM fails?"**
   Chain: Qwen gateway → Gemini → knowledge-base template. The chat NEVER crashes and always answers (with `used_llm` flag shown in UI). (Prashant)
3. **"How is the chatbot trained?"**
   It's not fine-tuned — it's **RAG**: 43 curated FAQs embedded and ranked per question, then the LLM answers with those as context. Explainable + no hallucinated steps. (Prashant)
4. **"Where does the data come from?"**
   Synthetic generator (`generate_synthetic.py`) mimics real fraud patterns (amount bursts, new accounts, night txns); schema seeded via `seed_data.py`; all in Supabase. (Gaurav/Ritik)
5. **"How do you handle privacy?"**
   Victims chat with **no login** (RLS only allows insert/select on chat tables); analysts are managed via Admin; keys live in `.env`/secrets (gitignored); Supabase secret rotated after demo. (Gaurav/Divyanshu)
6. **"Why Streamlit AND React?"**
   Streamlit = fast, safe command center for judges/demo (already live); React = premium product UI. Both share the same FastAPI backend. (Satyam)
7. **"How do you test it?"**
   26 pytest unit tests + full AppTest E2E against live Supabase (create→reset→remove analyst proves real coverage). (Divyanshu)
8. **"Is it deployed?"**
   Yes — Streamlit Cloud live at https://ffmitra.streamlit.app; React+FastAPI single-service Docker ready for Render. (Satyam)

---

## 11. SCREENSHOT CHECKLIST (final pass before the PPT)

- [ ] Login page (Streamlit + React)
- [ ] Command Center dashboard with glowing metrics
- [ ] Transactions table with APPROVE/REVIEW/BLOCK badges
- [ ] Investigate page: risk score + reasons list
- [ ] Fund Trail graph (React graph + Streamlit graphviz)
- [ ] Link Analyzer result (score + red flags)
- [ ] Victim Chat: AI reply + REC waveform + voice transcript
- [ ] Admin tab: create/reset/remove analyst toasts
- [ ] System health panel (Supabase ✅ / Qwen ✅)
- [ ] CSV download dialog
- [ ] Terminal: `pytest` 26 passed + E2E lines
- [ ] Terminal: `test_chat.py` conversation
- [ ] Supabase Table Editor (transactions/flagged_accounts)
- [ ] Architecture diagram (draw once: React/Streamlit → FastAPI → Supabase/ML/RAG/Qwen)