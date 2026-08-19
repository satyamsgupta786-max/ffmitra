# SIH INTERNAL ROUND 2026 — MASTER PRESENTATION PACKAGE (PART 2/3)
## PART 6 — CYBERSECURITY THREAT MODEL
## PART 7 — FEASIBILITY & SCALABILITY
## PART 8 — VALIDATION & EVIDENCE PLAN
## PART 9 — DEMO SCRIPT

---

# PART 6 — CYBERSECURITY THREAT MODEL

## 6.1 Attack surface map
1. **Public chat endpoints** (`/api/chat/session`, `/message`, `/voice`) — no auth, no rate limit today
2. **React web app** — client bundle contains the **publishable** Supabase key (by design); RLS is the real boundary
3. **FastAPI** — 10 routers; CORS allows localhost origins; `/api/admin/*` password-gated
4. **Supabase** — Postgres + Auth + RLS; publishable vs secret key split
5. **LLM gateways** — Qwen campus gateway (shared, ~15 students), Gemini (denied/quota)
6. **Simulator endpoint** (`POST /api/simulator/run`) — can inject data
7. **Streamlit app** — analyst login via Supabase auth

## 6.2 Threat table (threat → surface → attack → impact → mitigation → residual risk)

| # | Threat | Attack surface | Possible attack | Impact | Mitigation | Residual risk |
|---|---|---|---|---|---|---|
| T1 | Victim privacy breach | RLS policies on `chat_sessions`/`chat_messages` (anon SELECT = true) | Any anonymous user queries all victim conversations via REST | **High — legal (DPDP) + trust collapse** | Tighten RLS: remove anon SELECT; scope reads by session token/device key; encrypt sensitive fields | Currently **NOT implemented — must fix before real deployment** |
| T2 | Analyst account takeover | Supabase Auth login | Phishing/credential stuffing; weak passwords | Moderate — attacker sees cases, changes risk decisions | Supabase Auth; strong-password policy; admin-API resets; **MFA (planned)** | Moderate until MFA lands |
| T3 | Secret key leakage | `.env`, git history, screenshots | Key committed or shared → full DB read/write | **Critical** | Keys gitignored; never committed (verified via git log); rotate after demo | Rotation discipline is manual — rotate Supabase secret before final round |
| T4 | Prompt injection | Chat LLM | Victim message tricks Mitra into revealing prompt/system instructions or giving wrong rescue steps | Medium — wrong guidance could worsen a victim's situation | Strict system prompt; RAG grounding; 220-word cap; no tool access; output templating | Low-medium — LLM misuse is bounded but not zero; monitor |
| T5 | API abuse / cost burn | Public chat + voice endpoints | Bot floods messages → LLM gateway quota burn, DB spam | Medium — availability + shared gateway fairness | Rate limiting per IP/session (planned); cheap keyword pre-classification; per-session caps | Moderate today (no rate limit yet) |
| T6 | XSS via LLM/chat content | Chat rendering (React + Streamlit) | Malicious content in replies (LLM or user) executes in victim's browser | Medium | React escapes by default; Streamlit `md_light()` uses `html.escape` before injection; no raw HTML passthrough | Low |
| T7 | MITM / eavesdropping | All HTTP traffic | Sniff chat or login on public Wi-Fi | Medium | HTTPS everywhere (Streamlit Cloud, Render); local dev is localhost-only | Low |
| T8 | Replay / injection of transactions | `transactions` API | Attacker inserts fake transactions to manipulate scores | Medium — analyst trust broken | Write paths are internal/seed-only today; when bank feed lands: signed API tokens + idempotency keys | Low today (no public write path) |
| T9 | DoS of analyst dashboards | FastAPI | Flood `/api/dashboard/*` | Low-medium — public demo unavailable | Hosting provider rate limits; cached KPIs; queue-based scoring | Low |
| T10 | Insider threat | Admin endpoints | Analyst resets others' passwords, removes accounts | Medium | Admin actions are password-gated; **audit log (planned)** | Moderate — no audit trail yet |
| T11 | Model/data poisoning | FAQ corpus + training data | Malicious FAQ injected → Mitra teaches wrong steps | Medium | Corpus is curated/seed-controlled; synthetic data generator is deterministic; no user-written corpus input | Low now (closed corpus) |
| T12 | Supply chain | npm/pip dependencies | Compromised package | Varies | `package-lock.json` committed (frontend); pip deps pinned in requirements (partially); upgrade cadence | Low-medium |
| T13 | Misconfiguration | Streamlit secrets / Cloud env | Weak secrets, exposed `APP_SECRET` | Medium | Secrets via platform secret manager; `APP_SECRET` marked change-me | Low |
| T14 | Campus gateway dependency | Qwen gateway | Gateway down/slow/shared load | Medium — chat degrades | Gemini fallback + KB template; cooldown logic; streaming (planned) | Medium until independent LLM exists |

## 6.3 If an attacker tries to break our system — what happens?
- **Try to read all victim chats (T1):** Today they *could* (anon SELECT) — we admit it and it's fix #1. After fix: only the owning device/session reads its own conversation.
- **Try to steal the secret key (T3):** It's not in git. It's not in the browser bundle (only publishable key ships). They'd need the deployment console — that's the boundary.
- **Try to make Mitra give wrong advice (T4):** Prompt hardening + grounding + cap bounds it; a deterministic KB fallback means even a fully compromised LLM degrades to safe, curated steps.
- **Try to flood us (T5):** Today partially possible (no rate limit) — acknowledged, planned; LLM quota is the natural brake.

## 6.4 What we will NOT claim
- "100% secure" — never say it.
- "Unbreakable RLS" — we found a real gap ourselves; saying it first is a strength, not a weakness.

---

# PART 7 — FEASIBILITY & SCALABILITY

## 7.1 Technical feasibility
- **Built:** backend (10 routers), two frontends, RAG, ML, graphs, tests — all working.
- **Deployable:** single Docker image (frontend built into FastAPI static serve) → Render/VPS; Streamlit Cloud already live.
- **Verdict:** technically feasible TODAY at pilot scale; no invention required.

## 7.2 Economic feasibility
- **Current cost: ₹0/month** (Supabase free tier, Streamlit free, campus Qwen gateway).
- **Pilot (10k txns/day):** VPS ~₹1,200-2,500/mo (2 vCPU/4GB) + Supabase Pro ~₹1,500/mo (optional) + domain ~₹800/yr.
- **LLM at scale:** campus gateway free; independent path = hosted OpenAI-compatible endpoint or self-hosted small model (~₹1,500-4,000/mo at pilot volumes).
- **Monetization (honest):** licensing to banks/CEN units, per-analyst SaaS, government pilot funding (SIH/KAVACH grants). Not required for the internal round.

## 7.3 Operational feasibility
- **Who maintains:** college CoE/CCE students under faculty; CEN unit liaison for pilot.
- **Runbook exists?** `start-dev.ps1`/`start-host.ps1`, seed scripts, tests — yes, a fresh machine is up in ~10 minutes.
- **Ops risk:** single maintainer knowledge; document the runbook.

## 7.4 Infrastructure feasibility
- Postgres (managed Supabase) — indexes exist on `txn_time`, `source_ref`, `dest_ref`.
- Realtime via Supabase channels — fine at dashboard scale.
- Static SPA + API on one process — fine; split at scale.
- **No queue/broker today** — scoring is synchronous; fine at pilot, queue needed >10k txns/day.

## 7.5 Security feasibility
- RLS + auth exist; the anon-SELECT gap is fixable in a day (policy update, no code change).
- Secret hygiene proven (nothing secret in git history).
- Threat model documented (Part 6) — that IS the security deliverable for an internal round.

## 7.6 Legal/privacy feasibility
- DPDP Act 2023: personal data minimization, consent, purpose limitation — chat stores minimal PII; victims identified by session only.
- IT Act 2000 §66D (punishment for cheating by impersonation) — the fraud itself; we're a detection tool, not involved in enforcement.
- Integration with official channels (1930, NCRP) is an advantage, not a risk.
- **Caution:** real bank data needs a data-sharing agreement — that's the pilot gating item.

## 7.7 Scalability at three levels
| Scale | What works | Bottleneck | Fix |
|---|---|---|---|
| 100 users / 1k txns/day | Everything, current architecture | None | — |
| 10k users / 10k-50k txns/day | API + Postgres with existing indexes | Sync scoring latency; LLM latency on chat; single process | Add queue (Redis/Celery or FastAPI+ARQ) for scoring; rate limit chat; cache KPIs; paginate |
| 1M users / 10M txns/day | Partitioned tables, read replicas, batch scoring workers, CDN for SPA | LLM cost; realtime channel fan-out; Postgres writes | Partition by time; replica for dashboards; precomputed aggregates; dedicated ML serving; budget LLM with grounding-only queries |
**Honest position:** 10k/day is comfortably reachable on current architecture + a queue; 1M needs standard Postgres practices we've specified but not built.

---

# PART 8 — VALIDATION & EVIDENCE PLAN

## 8.1 Claim vs evidence table

| Claim | Evidence we HAVE | Evidence MISSING | How to validate (before the round) |
|---|---|---|---|
| "Fraud costs ₹1,453 crore in 2024" | — | **Source citation needed** | Find the official source (Ministry of Finance/RBI/NCRB/FIU 2024-25 annual report); put source + year ON the slide; if cannot verify, say "RBI/NCRB report 2024-25 (verify)" or remove the number |
| "Recovery rate < 5% for UPI fraud" | — | Source | Replace with verified stat or drop; never invent |
| "43 FAQs cover major fraud types" | Corpus exists (43 docs, 3 categories) | Mapping to official categories | Print the corpus list; map each FAQ to NCRP/RBI fraud category names; count per category on the slide |
| "Chat latency 2-9s" | Informal measurements | A proper table | Run 10 messages × 3 categories; record per-call latency (Qwen + fallback); screenshot table |
| "Retrieval picks correct FAQs" | 3/3 distinct questions tested | Larger sample | Test 10 questions (1 per FAQ category); record source question matched; screenshot |
| "Scoring works" | 127 synthetic txns scored, 5 flagged | Precision/recall on real data; confusion matrix | Run model on hold-out split of synthetic data; screenshot confusion matrix + ROC-AUC; label data as synthetic |
| "26 tests green" | Yes (run output) | — | Run `pytest -q` live during Q&A if asked; have output screenshot |
| "E2E works against live Supabase" | Yes (test_app.py output) | — | Same as above |
| "Voice works" | **Currently NO** (Gemini denied) | Working STT | Choose ONE: (a) local STT fallback (e.g., faster-whisper small, ~1GB model, offline, free) wired into `/voice`; or (b) remove voice from the demo and say "STT is Gemini-blocked; we use text" honestly. **Do not fake it.** |
| "Analyst admin works" | Yes (create/reset/remove E2E) | — | Screenshot the three toasts |
| "System health accurate" | Yes (Qwen probe 200) | — | Live screenshot in demo |
| "Secure" | Threat model + key hygiene | Pen-style review; rate limiting | Document the RLS fix; add basic rate limit on chat (10 req/min/IP) — 1 hour of work; screenshot policy SQL |
| "Scalable to 10k/day" | Architecture analysis | Load test | Optional quick win: `locust`/`ab` 200 concurrent requests against `/healthz` + `/api/transactions`; screenshot results; state limits honestly |

## 8.2 Evidence pack checklist (build before the round)
1. [ ] Latency measurement table (10 runs) — screenshot
2. [ ] Retrieval test table (10 questions → sources) — screenshot
3. [ ] Confusion matrix + ROC from synthetic hold-out — screenshot
4. [ ] pytest output (26 passed) — screenshot
5. [ ] E2E test output — screenshot
6. [ ] Supabase Table Editor (transactions/flagged) — screenshot
7. [ ] RLS policy screenshot (after fix) — screenshot
8. [ ] Load-test summary (if done) — screenshot
9. [ ] Source citations for both statistics — on-slide footnote
10. [ ] 2-minute offline demo recording (browser, highest quality) — for backup

## 8.3 Honesty rules
- Every number on a slide is either measured, sourced, or labelled "synthetic/assumption".
- If asked about something not implemented: *"Not implemented yet in the prototype. Our plan is…"* — never bluff.

---

# PART 9 — DEMO SCRIPT (3 minutes, live)

## 9.1 Exact sequence & narration

| Step | Click/action | Say (verbatim-ish) | Technical detail to reveal |
|---|---|---|---|
| 1 | Open **React app** (`http://localhost:8000`) → Victim Chat | "This is the live system. Watch a victim message." | Same backend as Streamlit |
| 2 | Type: *"Someone called me from the police and asked me to pay bail money"* → Send | "Notice the ✨ AI chip and the CRITICAL badge. The reply leads with 'Act fast' — bank freeze, then 1930." | RAG: question ranked against FAQ corpus; urgency from keyword rules |
| 3 | Ask second question: *"Is this my bank asking for my UPI PIN?"* | "See? Different question, different grounded answer — not a script." | Retrieval picks a different FAQ; `used_llm` flag |
| 4 | Go to **Investigate** → enter a flagged account → show score + reasons | "Analyst side: score 0.87 — and here are the human-readable reasons." | Weighted formula: 0.6·ML + 0.1·anomaly + 0.3·rules |
| 5 | Click **Fund Trail** → show graph | "The money moved through four accounts in eleven minutes — here's the trail." | NetworkX BFS, flow aggregation |
| 6 | Open **Link Analyzer** → paste `http://bit.ly/kyc-refund-update` → Analyze | "Link score 87, six red flags." | Heuristic scorer (TLD, shortener, keywords) |
| 7 | Open **Streamlit Command Center** → System health + CSV export | "Same backend, command center view: system health shows Supabase ✅, Qwen ✅; one click exports the CSV." | Health probes; download pipeline |
| 8 | If time/network allows: run `pytest` (pre-open terminal) | "And our tests — 26 green, plus the E2E that just created, reset, and removed an analyst live." | AppTest E2E |

## 9.2 What NOT to show
- Voice/mic recording (broken today) — unless you implement local STT first (Part 8.1).
- Any page that is slow or untested in rehearsal.
- Supabase dashboard internals unless asked (keep it 5 seconds if asked).

## 9.3 What to have pre-loaded
- Both apps open in tabs, logged in, BEFORE the demo starts.
- The exact messages/URLs ready to paste (no typing from memory).
- Terminal with `pytest -q` output ready to show.

## 9.4 Failure plans
| Failure | Recovery |
|---|---|
| Internet down | Play the 2-minute recorded video (backup) — "this is the live system, recorded 2 hours ago" |
| Qwen gateway slow | Skip chat steps, go straight to investigate + fund trail + link analyzer (no LLM needed) |
| Supabase down | Show recorded video; keep talking about architecture |
| Demo shows a bug | "That's a real bug — and it's honest. Here's the fallback path [show KB reply]. This is exactly why we test." (Never fake a fix) |
| Time running out | Cut steps 3 and 8; keep 1, 2, 4, 5, 6, 7 |

## 9.5 Backup demo plan (screenshots/video)
- Record the full flow with OBS/screen recorder at 1080p, ~3 minutes, both apps + pytest run.
- Have a slide with 6 screenshots (chat reply, reasons, fund trail, link score, health, CSV) as a "demo in screenshots" fallback.