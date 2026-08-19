# SIH PROJECT INFORMATION — FFMITRA

## AI-Based Financial Fraud Detection & Prevention Platform

---

**SIH Problem Statement (KAVACH PS-26 style):**

> *"Design and develop an AI-based system for the detection and prevention of financial frauds, including real-time fraud analytics, detection, and prevention across banks, UPI, cards, and digital payment systems."*

**Our proposed solution:**

FFMitra — a two-sided platform:
1. **For victims/citizens:** an always-on AI assistant ("Mitra") that gives instant, step-by-step rescue guidance in Hinglish — via text or voice notes — for UPI scams, "digital arrest" calls, OTP phishing, and fake investment apps (block bank, dial 1930, file NCRP complaint).
2. **For bank analysts/police:** a Command Center + React dashboard with ML-scored transaction risk, fund-trail graphs, a URL/link phishing analyzer, case management, realtime alerts, CSV reports, and analyst team administration.

**What makes our solution different:**

- **Hybrid, explainable scoring** — ML (XGBoost) + anomaly + 20+ interpretable rules blended with weights (0.6/0.1/0.3), every decision returns human-readable reasons (no black box)
- **RAG-based AI assistant** — grounded on a curated 43-FAQ fraud corpus (no hallucinated steps), urgency-aware replies, Hinglish empathy, voice-note support
- **Dual frontends, one backend** — premium React web app AND a Streamlit Command Center sharing the same FastAPI + Supabase stack
- **Network analytics** — multi-hop fund-trail graphs + lightweight framework-free link scorer used by both apps
- **Victim-first design** — chat needs no login (RLS-scoped), 1930 helpline always one tap away

**Current prototype/demo:**

Fully working end-to-end. Live at **https://ffmitra.streamlit.app** (Streamlit Cloud) and locally as a hosted React app (`start-host.ps1` → `http://localhost:8000`). 127 seeded transactions, 5 flagged accounts, real Qwen-gateway-powered AI chat, fund-trail graphs, CSV downloads, analyst management — all verified against live Supabase.

**Technology stack:**

- Backend: Python **FastAPI** (10 REST routers), Supabase (PostgreSQL + Realtime + Auth + RLS)
- ML: scikit-learn + **XGBoost**, pandas, numpy, SHAP-style reason extraction
- AI: **RAG** (43-doc FAQ corpus, 768-dim embeddings) + **Qwen via TCET CoE AI Gateway** (OpenAI-compatible) with Gemini fallback
- Graphs: **NetworkX** fund trail; link scorer (pure Python, framework-free)
- Frontend: **React + TypeScript + Vite + Tailwind** (framer-motion animations), **Streamlit** Command Center
- Deploy: Streamlit Cloud (live), Docker + Render config for single-service deploy

**Architecture:**

```
Victim / Citizen                    Bank Analyst / Police
   │  chat + voice                      │  React web app / Streamlit CC
   ▼                                   ▼
────────────── FastAPI (backend/app) ──────────────
  api/ (transactions, investigate, links, chat,
       flagged, cases, dashboard, admin, simulator)
   │            │             │              │
   ▼            ▼             ▼              ▼
Supabase   ML engine      Fund-trail      RAG + LLM
(Postgres) (features→      (NetworkX)     (Qwen gateway
 +realtime  rules→score                  → Gemini → KB
 +auth)     →reasons)                    fallback)
```

**Algorithms/models/security mechanisms:**

- Weighted hybrid score: `final = 0.6·ML_prob + 0.1·anomaly + 0.3·rule_hits`; thresholds **review ≥ 0.60, block ≥ 0.90**
- 22 engineered features (amount z-score, velocity, frequency, time-of-day, channel/merchant risk, account history)
- 20+ rule-based flags; anomaly detection via transaction-rate deviations
- Fund-trail BFS traversal (NetworkX) with flow aggregation
- URL scorer: TLD/domain-age heuristics, shortener detection, scam keyword scoring (0–100)
- Security: Supabase Auth (publishable vs secret key split), **RLS policies** (victims chat without login, analysts are managed users), secrets in gitignored `.env`, admin API for password resets

**Target users:**

1. Fraud victims and general citizens (especially elderly/low-digital-literacy users) — via the AI Mitra
2. Bank fraud/risk analysts and cybercrime police (CEN/DCP units) — via Command Center/React app

**Existing solutions/competitors:**

- Bank-side rule engines (FICO Falcon, IBM Safer Payments) — expensive, black-box, not explainable, analyst-only
- Fraud hotline 1930/NCRP portal — reactive, manual, no live guidance for the victim at the moment of the scam
- Generic chatbots (bank IVRs, helplines) — repetitive, no RAG grounding, English-only
- Our edge: explainable ML + free RAG assistant + dual dashboards + victim-first Hinglish voice UX — all in one platform

**Testing/validation/evidence:**

- **26 pytest unit tests** (scorer, rules, fund trail, chat) — all green
- **Full AppTest E2E** against live Supabase: victim message → login → Command Center → link analyzer → fund trail → CSV downloads → analyst create → password reset (200) → removal confirmed "gone from supabase: True"
- Live LLM probes: Qwen gateway 200 OK, embeddings 768-dim, chat `used_llm=True` with correct fraud guidance
- Verified production bug fixes: event-loop closure, JWT-expiry password bug, quota-exhaustion fallback (chat never crashes)

**Current limitations:**

- Gemini project banned/quota-exhausted → LLM falls back to Qwen gateway or knowledge base (works, but single-LM dependency on campus gateway)
- Voice transcription needs Gemini (no audio endpoint on Qwen gateway) → mic works via text transcription only when Gemini is available
- Synthetic (not real-bank) transaction data; no live bank/UPI integration
- Free-tier hosting (Streamlit) — no uptime SLA, single-instance

**Future scope:**

- Real-time UPI/payment API integration (NPCI/bank sandbox)
- Android/iOS app + WhatsApp bot for victims (1930-style reach)
- Multi-language support (12 official languages via TTS/STT)
- Streaming token-by-token chat, report auto-filing to NCRP portal
- Docker/Render production deployment with CI/CD, uptime monitoring
- Fine-tuned Hindi-English fraud model + customer-call transcription analytics

**Any measurable results:**

- Latency: chat reply ~2–9s (Qwen gateway), fallback < 2s
- Corpus: 43 curated FAQs, top-4 RAG retrieval — 3/3 distinct questions returned correct sources
- Scoring: 127 transactions scored, 5 flagged, 22 features, 26/26 tests green
- Fraud-burst simulator demonstrates near-real-time alert generation

**Number of team members:** 6

**Team member names and technical strengths:**

1. **Gaurav** — Backend architecture, FastAPI, Supabase/PostgreSQL, API design
2. **Ritik** — Machine learning, feature engineering, XGBoost, model training
3. **Krishna** — Graph analytics (NetworkX), fund-trail, URL/link phishing detection
4. **Prashant** — RAG pipelines, LLM integration (Qwen/Gemini), prompt engineering, voice
5. **Satyam** — React/TypeScript frontend, UI/UX animations, deployment (Docker/Render/Streamlit)
6. **Divyanshu** — Streamlit Command Center, enforcement automation, E2E testing

**Number of presentation slides:** *(fill: e.g. 15 — 1 title, 1 problem, 1 solution, 2 architecture, 1 per member module = 6, 1 demo, 1 results, 1 testing, 1 future scope, 1 thank-you)*

**Maximum presentation time:** *(fill: e.g. 15 minutes + 5 Q&A)*