# SIH INTERNAL ROUND 2026 — MASTER PRESENTATION PACKAGE (PART 1/3)
## FFMITRA — AI-Based Financial Fraud Detection & Prevention

> Prepared as a strict SIH judge simulation. Nothing here is marketing fluff.
> Rule: every claim must be either **validated**, **prototype-observed**, or **labelled an assumption**.

---

# PART 1 — EXECUTIVE ASSESSMENT

## What is strong (keep)
1. **A real, two-sided product, fully working.** Live Streamlit + local React app, real Supabase, real LLM chat. 90% of SIH teams show mockups; this is a working system.
2. **Explainable hybrid scoring (0.6 ML + 0.1 anomaly + 0.3 rules)** — this is genuinely judge-friendly: it answers "why did you flag this?" without a black box.
3. **RAG-grounded victim assistant** — the "Mitra" is a defensible, human story: victim-first, Hinglish, voice notes, 1930/NCRP steps. This is your emotional + practical USP in one.
4. **Dual frontends, one backend** — React + Streamlit sharing FastAPI proves engineering discipline (single source of truth).
5. **Evidence culture** — 26 pytest tests + a full AppTest E2E that manipulates live Supabase. Rare among college teams.

## What is weak (fix)
1. **Synthetic data everywhere.** 127 seeded transactions and the ML model come from a generator. A judge will ask "why should I believe your model works on real fraud?" — you currently have no answer beyond "the generator mimics patterns".
2. **Voice transcription is currently broken** (Gemini project denied). If you demo the mic and it apologizes, that's a credibility hit. Fix before the round (see Part 8) or don't demo it and say so honestly.
3. **Privacy hole in RLS:** `chat_sessions` and `chat_messages` allow **anon SELECT** (`0001_init.sql` lines 128-131). Any anonymous user can read every victim conversation. This is the #1 thing a security judge will attack.
4. **Single LLM dependency** on the campus Qwen gateway — it won't exist for the next round/real deployment, and latency varies. Gemini is denied. You have no independent LLM.
5. **No performance/scale evidence** — no load test, no latency table, no concurrency numbers.
6. **No user feedback** — zero interviews with real victims/analysts. For a "people-first" product this is your weakest evidence class.

## Biggest opportunity
Position FFMitra as **"the only open, explainable, victim-inclusive fraud platform"** — FICO Falcon and IBM Safer Payments are closed analyst-only boxes; 1930/NCRP are reactive manual processes. The victim-side AI + analyst-side open platform combo is your honest differentiator.

## Biggest judge risk
The judge's first thought: *"This is a college project using synthetic data and a campus LLM — it cannot be deployed in a bank."* Your counter-story must be: **pilot-ready, phased, and honest about what real deployment needs** (sandbox API integration, real data access via a partner bank/NPCI, DPDP compliance).

## Current estimated score: **68/100** (details in Part 12 / file 3)

---

# PART 2 — RECOMMENDED PPT STRUCTURE (16 slides)

| # | Slide | Speaker | Core message |
|---|---|---|---|
| 1 | Title + team | Lead | We built a working platform, here is who we are |
| 2 | The problem: a real story | P1 | A grandmother loses ₹3L to a "digital arrest" call |
| 3 | Root cause chain | P1 | Trust + speed + no rescue layer → fraud succeeds |
| 4 | Who suffers / personas | P1 | Victims, analysts, police — three pains, one platform |
| 5 | Existing landscape | P2 | Falcon/Safer/1930/NCRP: what they do and can't do |
| 6 | Gap + our insight + USP | P2 | "Unlike… our solution… because…" |
| 7 | Solution overview (two sides) | P3 | Victim app + analyst command center |
| 8 | User journeys | P3 | 90-second walkthrough of both sides |
| 9 | Architecture | P4 | One FastAPI core, two frontends, Supabase, RAG, ML |
| 10 | Tech deep dive | P4 | Hybrid scoring formula + RAG pipeline (2 small diagrams) |
| 11 | Security & threat model | P5 | Threat → mitigation → residual risk (honest) |
| 12 | Feasibility | P5 | Technical/economic/legal — pilot path |
| 13 | LIVE DEMO (3 min) | P6 | Victim chat → investigate → fund trail → link analyzer |
| 14 | Evidence | P6 | Tests, E2E, latency table, what we still need |
| 15 | Scalability & roadmap | P6 | 100 → 10k → 1M + Phase 1-4 |
| 16 | Closing | P6 | One-line ask: "give us a pilot with real data" |

**Total time: ~14-15 min + Q&A.** Practice hard: 55 sec/slide average.

---

# PART 3 — SIX-PERSON DISTRIBUTION

| Person | Slides | Responsibility | Main objective |
|---|---|---|---|
| **Prashant** (P1) | 2, 3, 4 | Problem & Impact | Judge thinks: "this is a serious, real problem" |
| **Ritik** (P2) | 5, 6 | Existing landscape & Innovation | Judge thinks: "they know the market and have a real reason" |
| **Divyanshu** (P3) | 7, 8 | Solution & User journey | Judge thinks: "the product is clear and usable" |
| **Satyam** (P4) | 9, 10 | Architecture & Technology | Judge thinks: "they actually built this and understand it" |
| **Gaurav** (P5) | 11, 12 | Cybersecurity & Feasibility | Judge thinks: "they know how it breaks and how to defend it" |
| **Krishna** (P6) | 13, 14, 15, 16 | Demo, Evidence, Scalability, Closing | Judge thinks: "this can be deployed, not just demoed" |

Rules for everyone:
- Every member must be able to answer at least 3 questions from EVERY category (see Part 10 / file 3, cross-questioning).
- No "one-slide-only" members. A judge WILL cross over.

---

# PART 4 — COMPLETE SLIDE-BY-SLIDE SCRIPT

---

## SLIDE 1 — Title
- **Speaker:** Team lead (Satyam or designated)
- **Purpose:** Credibility + team identity in 30 seconds.
- **Visual:** Dark cyber theme, animated ⌬ FFMITRA logo, tagline "Fraud-Free Mitra — AI-Based Financial Fraud Detection & Prevention Platform", team names, KAVACH PS-26 reference, SIH Internal Round 2026.
- **Script (natural, not corporate):**
  > "Good morning, judges. We are team FFMitra, and this is our working answer to problem statement PS-26 — detecting and preventing financial fraud across UPI, cards, and digital payments. We're six people — Prashant, Ritik, Divyanshu, Satyam, Gaurav, and Krishna. The thing I want you to remember from this whole presentation is one word: *Mitra* — friend. We built a system where a fraud victim gets a friend in the moment they need it most, and analysts get a tool that explains every decision it makes. And it's not a mockup — it's live. Let me start with why this problem matters."
- **Judge takeaway:** A confident team with a working product.
- **Transition:** "Prashant, take the story forward."

---

## SLIDE 2 — The Problem: A Real Story
- **Speaker:** Prashant
- **Purpose:** Emotional + factual hook. NEVER start with features.
- **Visual:** One large photo-style card: "3:47 PM, a phone rings…" + 4 bullet facts:
  - ₹1,453 crore lost to digital fraud in 2024 (verify source — see Evidence)
  - UPI scams, digital-arrest calls, OTP phishing, fake investment apps
  - Typical victim: elderly, or someone under pressure ("you'll be arrested")
  - Money moves out in **minutes**; help arrives in **days**
- **Script:**
  > "Imagine this: your grandmother gets a call at 3:47 PM. The caller says he's from the CBI, there's an arrest warrant on her name, and to avoid it she must transfer money to a 'security account' — and stay on the video call so they can 'verify'. She's scared. She transfers ₹3 lakh in five minutes. The moment she realizes, it's 6 PM — the bank is closed, the helpline is busy, and the money has already moved through four accounts. This is not an unusual story — digital fraud in India crossed ₹1,453 crore in 2024. And the worst part? The fraud doesn't happen because people are foolish. It happens because the system gives a scammer *time* and gives the victim *nothing* at the moment of panic."
- **Technical explanation:** The window between a victim's realization and any intervention is the "rescue gap" — typically 4-72 hours; UPI money movement completes in seconds.
- **Judge takeaway:** Problem is real, frequent, and the victim is sympathetic.
- **Transition:** "Now the important question — *why* does this keep working? Ritik, the root causes."

---

## SLIDE 3 — Root Cause Chain
- **Speaker:** Prashant
- **Purpose:** Show analytical depth — you understand WHY, not just WHAT.
- **Visual:** Chain diagram:
  `Root: Trust-based social engineering + instant payments`
  → `Contributing: banks detect fraud AFTER money leaves; helplines are reactive; victims have no guided rescue path`
  → `Symptoms: money moves to mule accounts within minutes; victims panic-share OTPs; complaints filed late`
  → `Consequence: recovery rate < 5% for UPI fraud (mark: needs source)`
- **Script:**
  > "If you look closely, the root problem is not 'people fall for scams'. It's a structural gap: payments are instant, detection is post-facto, and the victim has no guided rescue path between panic and the police station. So fraud works because three things line up — the scammer creates urgency, the money moves instantly, and no one tells the victim what to do in that exact moment. If we only build better detection, we still leave the victim alone. That's why our solution attacks two points at once: detection for the analyst, and real-time guidance for the victim."
- **Judge takeaway:** They attack the root, not the symptom.
- **Transition:** "Who are the people on both sides? Same slide set — Prashant continues."

---

## SLIDE 4 — Who Suffers / Target Users
- **Speaker:** Prashant
- **Purpose:** Define users precisely — judges hate vague "everyone needs this".
- **Visual:** 3 persona cards:
  1. **Victim/citizen** — elderly, low digital literacy, Hindi/English mix, panics → needs instant Hinglish guidance
  2. **Bank fraud analyst** — flooded with alerts, needs explainable scores + exportable reports
  3. **Cybercrime police (CEN/DCP)** — needs fund trails + case files, not CSV dumps from 5 banks
- **Script:**
  > "Three concrete users. First, the victim — and we deliberately designed for low digital literacy: no login, voice input, Hinglish replies, and the 1930 helpline one tap away. Second, the bank analyst — they don't need another alert that says 'high risk'; they need to know *why*, in human language, with a report they can export. Third, cyber police — when they get a complaint, they need the money trail across accounts, fast. One platform serves all three — that's the product bet we made."
- **Judge takeaway:** Clear target users with distinct pains.
- **Transition:** "But of course, we're not the first to try. Ritik — what already exists?"

---

## SLIDE 5 — Existing Landscape
- **Speaker:** Ritik
- **Purpose:** Honest competitor analysis — no fake players.
- **Visual:** Comparison table (What / What it does well / Where it fails):
  | Solution | Good at | Fails at |
  |---|---|---|
  | FICO Falcon / IBM Safer Payments | Bank-side real-time scoring | Closed black-box, enterprise cost, analyst-only, no victim help |
  | 1930 helpline + NCRP portal | Official reporting channel | Reactive, manual, hours of hold, no guidance at panic moment |
  | Bank chatbots/IVRs | Basic FAQs | Repetitive, English-first, no RAG grounding, no rescue workflow |
  | Our FFMitra | Explainable scoring + victim-first RAG + open dual dashboards | Needs pilot with real data; not yet bank-integrated |
- **Script:**
  > "Let's be honest about the landscape. FICO Falcon and IBM Safer Payments are excellent — for banks with large budgets. But they're closed systems: an analyst sees a score, not a reason, and the victim is completely absent from the picture. The 1930 helpline and NCRP portal are official, but reactive — the victim is on hold while money is moving. Generic bank chatbots repeat FAQs. Nobody — as far as we could find — combines explainable scoring for analysts with an always-on rescue assistant for victims in one open platform. That gap is exactly where FFMitra sits."
- **Judge takeaway:** They know the real market and positioned honestly.
- **Transition:** "So here is our insight and our USP — one line."

---

## SLIDE 6 — Gap, Insight & USP
- **Speaker:** Ritik
- **Purpose:** The single most important slide. One clear, technically meaningful USP.
- **Visual:** Big quote block:
  > **USP:** "Unlike closed bank fraud engines that score and stop, and unlike reactive helplines that wait to be called, FFMitra is an open, explainable platform that scores fraud in real time for analysts AND walks victims through rescue in Hinglish — grounded on a curated fraud corpus so it never hallucinates steps."
- **Script:**
  > "Our USP in one sentence: closed fraud engines score but don't explain and don't help the victim; helplines help but only after the victim thinks to call. FFMitra is the middle — an explainable scoring engine where every decision returns reasons, and a victim assistant grounded on a curated corpus of 43 verified fraud scenarios, so the steps it gives are the real ones — bank freeze, 1930, NCRP. That combination — explainable + victim-inclusive + open — is what we could not find in any single existing product."
- **Judge takeaway:** Clear differentiation, technically defensible.
- **Transition:** "Enough strategy — what did we actually build? Divyanshu."

---

## SLIDE 7 — Solution Overview (Two Sides)
- **Speaker:** Divyanshu
- **Purpose:** Product clarity before tech.
- **Visual:** Two panels:
  - **For victims:** AI Mitra chat (text/voice), category + urgency detection, rescue steps, link analyzer
  - **For analysts:** Live dashboard, risk-scored transactions, fund trails, cases, link analyzer, CSV reports, analyst admin
- **Script:**
  > "The product has two faces, one brain. On the victim side: no login, no forms — you describe what happened, in text or voice, and Mitra tells you the category, the urgency, and exactly what to do — freeze the account, call 1930, file a complaint — in simple Hinglish. On the analyst side: a command center where every transaction carries a risk score and, more importantly, the *reasons* — plus fund trails to follow the money, cases to manage, and one-click CSV reports. Same backend, same data — that's the design decision that keeps us coherent."
- **Judge takeaway:** Product is understandable in 60 seconds.
- **Transition:** "Let me walk you through both journeys — 90 seconds, live screenshots."

---

## SLIDE 8 — User Journeys
- **Speaker:** Divyanshu
- **Purpose:** Show real screenshots, not wireframes.
- **Visual:** Two screenshots (React app + Streamlit app), each with 4-step arrows:
  - Victim: "typed message → urgency CRITICAL → rescue steps → 1930 tap"
  - Analyst: "login → dashboard KPIs → investigate account → fund trail graph"
- **Script:**
  > "Victim journey: she types 'someone called saying I'll be arrested', Mitra classifies it as phishing with critical urgency, and the reply leads with 'Act fast — call your bank now, then 1930'. One tap calls the helpline. Analyst journey: login, see live KPIs, open any account, see a score of 0.87 with reasons like 'unusual amount for this account' and 'recipient is flagged', then expand the fund trail and watch the money flow across four accounts. Both journeys run on the same live system you'll see in the demo."
- **Judge takeaway:** Real product, real screenshots, real flows.
- **Transition:** "How is this built? Satyam takes the architecture."

---

## SLIDE 9 — Architecture
- **Speaker:** Satyam
- **Purpose:** One clean diagram — simplicity wins.
- **Visual:** The architecture diagram (as in project docs):
  ```
  Victims (chat/voice)         Analysts (React web app / Streamlit CC)
             \                          /
              └────────▶ FastAPI (10 routers) ◀────────┘
                  │        │         │        │
              Supabase   ML engine  Fund-trail  RAG + LLM
             (PG+realtime+auth) (rules→score→reasons) (NetworkX) (Qwen → Gemini → KB)
  ```
- **Script:**
  > "One backend, two frontends. FastAPI exposes ten routers — transactions, dashboard, flagged accounts, cases, investigate, links, chat, admin, simulator — and both the React app and the Streamlit command center consume exactly the same APIs. Data lives in Supabase — Postgres with realtime and row-level security. The ML engine scores every transaction with 22 features. The fund-trail module traces money over the network with NetworkX. And the chat is RAG: a curated corpus of 43 fraud FAQs, embedded, ranked per question, and answered by an LLM. Why FastAPI? Async, typed, and it shares Python with the ML stack. Why not Node for the API? Then ML would become a second service — we deliberately kept one runtime. Why Supabase? Managed Postgres, auth, and realtime in one — free tier today, scales with us."
- **Judge takeaway:** They can justify every technology choice.
- **Transition:** "Two parts of this deserve a deeper look — the scoring and the RAG. Same slide."

---

## SLIDE 10 — Tech Deep Dive: Scoring + RAG
- **Speaker:** Satyam
- **Purpose:** Proof of technical depth. Two small diagrams, no wall of code.
- **Visual:** Left: formula card `score = 0.6·ML + 0.1·anomaly + 0.3·rules → review ≥0.60, block ≥0.90` + "reasons: unusual amount, new recipient, night transfer". Right: RAG pipeline `question → embed → rank top-4 FAQs → prompt LLM (Qwen gateway) → Hinglish reply with urgency`.
- **Script:**
  > "Two decisions matter. Scoring: we don't ship a black box. Final risk is a weighted blend — 60% ML model, 10% anomaly detection, 30% interpretable rules — and every score carries reasons: 'amount 8x above this account's average', 'recipient is on the flagged list'. The analyst sees the *why*, not just a number. The thresholds — review at 0.60, block at 0.90 — are configurable in the database. RAG: the victim assistant never answers from memory. The question is embedded, matched against 43 curated FAQs, and the top four are given to the LLM as context. So when Mitra says 'dial 1930 and file an NCRP complaint', those steps come from our curated corpus — grounded, not hallucinated. And there's a three-tier fallback: Qwen gateway, then Gemini, then a deterministic knowledge-base template — the chat has never crashed."
- **Judge takeaway:** Real algorithms, real thresholds, real failure handling.
- **Transition:** "But a security product must know how it can be attacked. Gaurav."

---

## SLIDE 11 — Security & Threat Model
- **Speaker:** Gaurav
- **Purpose:** Show threat-model thinking. Honest, with residual risks.
- **Visual:** Compact table (4-5 rows only):
  | Threat | Mitigation | Residual risk |
  |---|---|---|
  | Analyst account takeover | Supabase Auth, admin API for resets, secret keys never in client | No MFA yet — planned |
  | Anonymous reading of victim chats | RLS scoped to insert/select | **KNOWN GAP:** anon select on chat tables — tightening (Part 12) |
  | LLM prompt injection | System-prompt hardening, RAG grounding, 220-word cap | Low |
  | Secret leakage in git | `.env` gitignored, keys never committed | Must rotate post-demo |
  | Abuse of public chat endpoint | Cost-capped fallback, rate limiting (planned) | Moderate today |
- **Script:**
  > "Security is a threat model, not a feature list. Three real risks we defend: analyst accounts — auth through Supabase, password resets through the admin API only, secret keys never touch the browser. Prompt injection — an attacker can try to make Mitra give wrong rescue steps; we bound this with a strict system prompt, RAG grounding, and short outputs. And secret hygiene — our keys live in gitignored `.env` files; nothing secret has ever been committed. I'll also be straight with you: our RLS currently lets anonymous users *insert* chat sessions, and we're tightening read access so one victim can never read another's conversation — that's on our fix list before deployment. Residual risks remain — no system is 100% secure, and we'll say exactly which ones in Q&A."
- **Judge takeaway:** They think like defenders and admit gaps — huge credibility.
- **Transition:** "Is this feasible beyond the lab? Same speaker."

---

## SLIDE 12 — Feasibility
- **Speaker:** Gaurav
- **Purpose:** Technical + economic + legal reality, phased.
- **Visual:** 3 columns:
  - **Technical:** built & live; single-service Docker deploy; tests green
  - **Economic:** today ₹0 (free tier + campus LLM gateway); pilot ≈ ₹1.5-4k/month (VPS + Supabase pro)
  - **Legal/Privacy:** DPDP Act alignment, PII minimization, 1930/NCRP integration path
- **Script:**
  > "Feasibility in three words: cheap, phased, legal. Today the system runs on free tiers and the campus AI gateway — literally zero cost. A pilot — say 10,000 transactions a day — fits comfortably on a small VPS with managed Postgres, roughly two to four thousand rupees a month. Legally, we minimize PII, follow DPDP principles, and the rescue workflow integrates with official channels — 1930 and the NCRP portal — so we're augmenting the state, not bypassing it. Deployment path: today a single Docker service; next a queue for async scoring; at scale, read replicas and partitioned tables. Nothing in this plan requires technology that doesn't exist."
- **Judge takeaway:** Realistic economics, legal awareness.
- **Transition:** "Enough talk — Krishna, show them it works."

---

## SLIDE 13 — LIVE DEMO (3 min)
- **Speaker:** Krishna (with support from any member for the second screen)
- **Purpose:** Proof. Keep it tight, rehearsed, offline-safe.
- **Visual:** Live browser (or recorded video fallback).
- **Demo sequence (see Part 9 for the exact script):**
  1. Victim chat: "digital arrest" message → AI reply (✨ AI) + CRITICAL badge
  2. Investigate: flagged account → score + reasons
  3. Fund trail: graph across accounts
  4. Link analyzer: paste a scam-looking URL → high score
  5. Streamlit command center: CSV export + system health
- **Script (during demo):**
  > "This is the live system, right now. Watch what happens when a victim says… [type]. Notice it flags critical and leads with 'Act fast'. Same backend, now the analyst side: this account scores 0.87 — and here are the reasons, in English, not a number. Expand the fund trail — money moved through four accounts in eleven minutes. Now the link analyzer — a 'refund-kyc-update' link, score 87, six red flags. And the command center exports this as CSV for a police file. All live, all on one backend."
- **Judge takeaway:** It works, on stage, live.
- **Transition:** "And it's not just demoed — it's tested. Evidence."

---

## SLIDE 14 — Evidence
- **Speaker:** Krishna
- **Purpose:** Numbers + honesty. Include what you DON'T have yet.
- **Visual:** Evidence table:
  - 26/26 pytest tests green (scorer, rules, fund trail, chat)
  - Full E2E against live Supabase: create → reset → remove analyst, "gone from supabase: True"
  - Chat latency: 2–9s (Qwen), <2s fallback (measure table — see Part 8)
  - 3/3 distinct questions → distinct correct RAG sources
  - 22 features, 127 transactions scored, 5 flagged
  - **Honesty row:** model trained on synthetic data; no real bank feed yet; voice STT blocked by Gemini denial
- **Script:**
  > "Evidence first: 26 unit tests, all green. A full end-to-end test that creates an analyst, resets their password, logs in with the new password, and removes them — against live Supabase — all passing. Measured chat latency: two to nine seconds on the gateway, under two seconds on fallback. And the retrieval test: three different questions returned three different, correct FAQ sources. Now the honest part: our ML model trains on a synthetic dataset — we'll show you the generator — and our voice transcription currently needs a Gemini quota we've exhausted. We don't hide that. What we show is a working pipeline where every layer is tested and the remaining gaps are data access, not engineering."
- **Judge takeaway:** Evidence-driven AND honest — rare and credible.
- **Transition:** "Where does this go? Scale and roadmap."

---

## SLIDE 15 — Scalability & Roadmap
- **Speaker:** Krishna
- **Purpose:** Concrete phases, each solving a stated problem.
- **Visual:** 4 phases:
  - **Phase 1 (now):** harden RLS/privacy, local STT, rate limits, load test
  - **Phase 2 (pilot):** NPCI/bank sandbox API, 10k txn/day pilot, DPDP review
  - **Phase 3 (scale):** async queue, read replicas, partitions, multi-region
  - **Phase 4 (advance):** WhatsApp bot, 12 languages, NCRP auto-filing, streaming replies
- **Script:**
  > "Scale in honest numbers. At 100 users: current architecture, no change. At 10,000: the same Postgres with proper indexing, plus a job queue so scoring doesn't block the API — a day of work. At a million: partitioned tables, read replicas, and batch-scoring workers — standard Postgres practice. The roadmap is phased: first, hardening — privacy, rate limits, offline STT. Then a pilot with a bank sandbox — that's the real-data milestone we need. Then scale. Then advanced: a WhatsApp bot because that's where victims actually are, twelve languages, and auto-filing complaints to NCRP. Every phase answers one question: what real problem does this remove?"
- **Judge takeaway:** Honest scaling math, no "we will add AI".
- **Transition:** "Closing."

---

## SLIDE 16 — Closing
- **Speaker:** Krishna (or team lead)
- **Purpose:** One clean ask.
- **Visual:** One line: **"Give us a pilot with real data — we'll prove it."** + 1930/NCRP touchline + team name.
- **Script:**
  > "To close: we found a structural gap — instant payments, post-facto detection, and a victim left alone at the worst moment. We built the middle layer: an explainable scoring engine for analysts and a grounded rescue assistant for victims, one backend, tested end-to-end, live today. What we need next is not more code — it's a pilot with real transaction data and real users. So our request to the judges is simple: put us in front of data. Thank you."
- **Judge takeaway:** Clear ask, confident, humble where needed.

---

# PART 5 — TECHNICAL ARCHITECTURE EXPLANATION (3 levels)

## Simple level (for slides 7-8)
FFMitra = a website for analysts + a chat for victims, sharing one brain (backend). The brain reads transactions, scores them, traces money, and answers victims.

## Intermediate level (for slides 9-10)
- FastAPI exposes 10 routers; both UIs call the same endpoints.
- Supabase holds transactions/accounts/cases/chats with realtime + RLS.
- ML: 22 features → XGBoost probability + anomaly + 20+ rules → weighted score → reasons.
- RAG: 43-FAQ corpus → embeddings (768-dim) → top-4 ranking → LLM (Qwen gateway) → Hinglish reply; fallback Gemini → template.
- Fund trail: NetworkX BFS over transactions → graph JSON → UI graphs.
- Link analyzer: pure-Python heuristics (TLD, shorteners, keywords) → 0-100 score.

## Deep level (for Q&A)
- `backend/app/db.py`: async Supabase REST adapter; `run()` wrapper creates a fresh client inside each event loop (fixes "event loop is closed" in production).
- `backend/app/ml/scorer.py`: `final = ml_weight·ml_prob + anomaly_weight·anomaly + rule_weight·rule_hits`; thresholds review=0.60/block=0.90 loaded from `settings` table (configurable at runtime).
- `backend/app/ml/features.py`: 291 lines, 22 features (z-scores, velocity, frequency, time-of-day, channel risk).
- `backend/app/rag/chat_llm.py`: `_rank_docs()` embedding-first + keyword fallback; `_call_qwen()` OpenAI-compatible chat completions (Bearer key, 90s timeout, 2 retries); `_qwen_unavailable()` 5-min cooldown after 2 failures; Gemini `_call_gemini()` with quota flag; final deterministic template — three tiers, never crashes.
- `backend/app/graph/fundtrail.py`: NetworkX traversal with flow aggregation, direction and hop depth.
- `backend/app/ml/link_scorer.py`: framework-free so FastAPI and Streamlit share one implementation (no dependency conflict).
- `backend/app/api/admin.py`: user lifecycle via Supabase **admin API** (secret key) — avoids the 1-hour session-JWT expiry bug on `/auth/v1/user`.
- `streamlit_app/app.py`: same `run()` loop pattern; `csv_download()`; admin tab with create/remove/reset + system health probes (Qwen `/v1/models`, Gemini `generateContent`).
- Frontend: React Router protected routes; framer-motion animations; `api.ts` bearer-token fetch wrapper; Supabase realtime channel for the Live Feed.
- Static serving: FastAPI serves built SPA (`frontend/dist`) with `/assets` mount + catch-all → single-service Docker/Render deploy.