# SIH INTERNAL ROUND 2026 — MASTER PRESENTATION PACKAGE (PART 3/3)
## PART 10 — JUDGE CROSS-QUESTIONS (110 Q&A BANK + CROSS-DEFENCE)
## PART 11 — RED-TEAM REVIEW
## PART 12 — FINAL SCORE & FIX LIST

---

# PART 10 — JUDGE CROSS-QUESTIONS

> Format per question: **Answer (20-40s)** · Counter-question · Counter-answer · Evidence to have.
> Golden rule: if not implemented → *"Not in the prototype yet. Our plan is…"*

## 10.1 PROBLEM & IMPACT (15)

**Q1. Why is this problem important NOW?**
A: Three accelerants: UPI volume exploded (billions of txns/yr), fraud moved to social engineering (digital arrest, OTP phishing), and official channels (1930/NCRP) remain reactive. The victim has nothing at the panic moment — that's the gap we fill.
Counter: "Wasn't this always true?"
Counter-A: Yes, but the scam-to-payment window shrank from days to minutes with instant payments; that's what makes a real-time victim assistant newly necessary.
Evidence: UPI growth + fraud stats (sourced).

**Q2. Who is your primary user — victim or bank?**
A: Both, but the victim side is our differentiator and the analyst side is our revenue path. One backend serves both; piloting with analysts is how we get real data, and the victim product rides the same pipeline.
Counter: "Then you're building two products."
Counter-A: Two frontends, one brain — 80% of the value (scoring, RAG, fund trail) is shared. The dual UI is ~20% extra, and it's why both audiences see value.

**Q3. What's the worst realistic consequence if this problem is unsolved?**
A: For the victim: unrecoverable life savings (recovery is rare). For the system: fraud funds flowing to organized networks, money laundering chains kept alive. For society: trust erosion in digital payments slows financial inclusion — the elderly just stop using UPI.

**Q4. What is the actual frequency?**
A: India's cyber-fraud complaints run in the millions per year; UPI frauds dominate. I'll give you the exact sourced number on that slide — we're not presenting unsourced figures.
Counter: "Which report?"
Counter-A: [Name the exact source on your slide — RBI/NCRB/FIU report, year, figure. If you can't verify, remove the number.]

**Q5. How does your solution reduce fraud, not just help after?**
A: Two mechanisms: (a) analyst scoring + fund trails catch and block BEFORE money launders (rules like "large amount to new recipient" fire at scoring time); (b) victim guidance reduces the window a scammer can keep exploiting the victim — stopping repeat payments and mule reporting via fund trails.

**Q6. Elderly users — will they really use a chat app?**
A: Honest answer: our prototype targets smartphone-savvy users first; the elderly phase (Phase 4) is WhatsApp + voice + 12 languages. Voice input today is designed exactly for that user — one tap, speak, get steps.
Counter: "So not for elderly yet?"
Counter-A: Correct — that's a Phase-4 capability; the architecture (voice pipeline, Hinglish prompt, no-login chat) is already in place.

**Q7. What's the user pain you measured?**
A: We have not done formal interviews yet — that's an honest gap. What we have: 1930/NCRP public documentation of complaint friction, and the fact that banks detect post-transfer. We are scheduling 5-10 user sessions before the next round.
Counter: "So no user research?"
Counter-A: Correct, not yet — it's in the evidence plan (Part 8). We won't pretend we have it.

**Q8. How fast must your system react to be useful?**
A: Chat: seconds (2-9s today). Scoring: should be sub-second at payment time — currently our scoring is sub-100ms per transaction in tests; real-time bank integration is Phase 2.
Counter: "Can you prove sub-100ms?"
Counter-A: Measured on synthetic load in tests; happy to show the benchmark — it's not yet a formal load test.

**Q9. What happens if the victim does nothing after the reply?**
A: The chat is guidance, not enforcement — same as a helpline. The analyst side carries enforcement (blocked accounts, alerts). We don't claim to force victims to act.

**Q10. Why should a bank trust your risk score over FICO's?**
A: We don't ask them to replace FICO — we complement: explainability (reasons in English), open stack, victim side, and a pilot path at a fraction of the cost. Real validation needs their data — that's the pilot we're asking for.
Counter: "So you're not better, just cheaper and transparent?"
Counter-A: Cheaper, transparent, and victim-inclusive — in risk scoring, explainability and coverage breadth are genuine differentiators for alert triage.

**Q11. Is the problem technical or social?**
A: Both. Technically: detection is post-facto and mule networks move money fast. Socially: urgency-based social engineering. Our solution is technical (scoring/trails) with a social interface (Mitra in Hinglish). The root is the missing layer between detection and the victim.

**Q12. What's the single metric that proves you help?**
A: Time-to-intervention: from victim realization to guided first action (freeze call). Today that's hours; our design targets minutes. We can't measure it yet — it needs user testing, which is why we asked for a pilot.

**Q13. Digital arrest is a specific scam — how general is your solution?**
A: The pipeline is scam-agnostic: category + urgency keywords, RAG corpus, rescue workflow. Digital arrest, OTP phishing, investment apps, courier scams — each is a corpus entry, not a code change. Adding a new scam type = adding FAQ docs.

**Q14. What if banks already have all this internally?**
A: Banks have closed scoring; they don't have an open victim layer, cross-institution fund trails (bank A can't see bank B's accounts), or analyst CSV/export workflows in one place. Cross-bank view is the structural gap — money moves across banks.

**Q15. Where does the money actually go?**
A: Mule accounts — 3-5 hops before withdrawal. That's precisely why the fund trail matters: single-account scoring misses the network; trail analysis exposes it.

## 10.2 TECHNICAL (15)

**Q16. Explain your scoring formula precisely.**
A: `final = 0.6·ML_prob + 0.1·anomaly_score + 0.3·rule_hits` where ML is XGBoost on 22 features, anomaly is transaction-rate deviation, rules are 20+ boolean flags. Decision: review ≥0.60, block ≥0.90. Thresholds live in the settings table — changeable at runtime.
Counter: "Why those weights?"
Counter-A: Chosen by rule-of-thumb + small grid search on the synthetic set; we show the search in the notebook. Real weights would be tuned on real data in a pilot — that's honest.

**Q17. Your model trains on synthetic data. Why should I believe it?**
A: You shouldn't fully — and we say that. The generator encodes documented fraud patterns (amount bursts, new-account spikes, night transfers, mule chains) so the pipeline is real; the numbers need real data. That's the pilot ask.
Counter: "So it's untested ML."
Counter-A: Tested end-to-end on synthetic distributions; unvalidated on real distributions. We distinguish those clearly.

**Q18. Why XGBoost, not deep learning?**
A: Tabular data, small dataset, and explainability: tree models give feature importance and are the practical SOTA for transaction tabular data in industry. DL would add compute and opacity without a demonstrated accuracy gain at our data scale.

**Q19. How does RAG prevent hallucination?**
A: It doesn't eliminate it; it grounds it. Top-4 corpus chunks + strict system prompt + 220-word cap + deterministic fallback. The rescue steps (1930, freeze, NCRP) are corpus content, not model memory.
Counter: "LLMs still hallucinate."
Counter-A: Agreed — that's why the final tier is a rule-based template with curated steps; the model can't invent a wrong helpline number because it can't exceed the corpus + cap.

**Q20. Why Qwen gateway instead of Gemini directly?**
A: Gemini's free quota exhausted/denied; the campus CoE gateway is OpenAI-compatible, verified 200 OK, and free. The abstraction (one chat-completions call) means swapping providers is a config change.
Counter: "Campus gateway is a crutch."
Counter-A: It's the pragmatic zero-cost path for the demo; production path is a hosted endpoint or self-hosted model — config-level swap, designed for it.

**Q21. How is the fund trail computed?**
A: NetworkX BFS from the suspect account over the transactions graph — configurable depth and direction; aggregates total flow per path. Complexity is O(V+E) per query; index on source/dest refs keeps it fast.
Counter: "Can't you just join the table?"
Counter-A: Joins only work for direct hops; multi-hop with direction + flow aggregation is exactly what the graph module adds.

**Q22. How does the link analyzer work?**
A: Pure-Python heuristics: suspicious TLDs, shortener domains, keyword scoring (kyc-update, refund, lottery), URL structure anomalies, non-HTTPS, IP hosts — weighted to 0-100 with reasons.
Counter: "Why not a trained model?"
Counter-A: No reliable labeled URL dataset at college scale; heuristics are auditable, framework-free, and shared between FastAPI and Streamlit without dependency conflicts.

**Q23. How do your two frontends stay consistent?**
A: Both call the same FastAPI routes — no duplicated logic. The only duplicated code is presentation. The link scorer is literally imported by both apps.
Counter: "Streamlit and React are redundant."
Counter-A: They serve different users: Streamlit = quick analyst command center (and our live demo surface), React = premium product UI. Same backend keeps them honest.

**Q24. What happens when the LLM fails?**
A: Three tiers: Qwen → Gemini → deterministic KB template. Cooldown logic (2 failures in 5 min → skip LLM) keeps latency <2s instead of hanging. Chat has never crashed; every tier is tested.
Counter: "So the 'AI' is often the template?"
Counter-A: The template is the safety net; live probes show Qwen answering with used_llm=True in normal operation.

**Q25. How do you store chat history and use it?**
A: Supabase `chat_messages` (session-scoped); last 6 messages feed the LLM as context — enables follow-ups like "what else should I do?" without retraining.

**Q26. What's in the 22 features?**
A: Amount z-scores vs account history, velocity (count/amount in rolling windows), time-of-day/seasonality, channel and merchant risk, recipient newness, device/IP flags, transaction-type mixes. Full list is in `features.py` — open it if you like.
Counter: "Which feature contributes most?"
Counter-A: On synthetic data: amount z-score and velocity dominate; we can show feature importance from the trained model.

**Q27. How do thresholds 0.6/0.9 get set?**
A: Runtime-configurable via the `settings` table — analyst can tune review/block without redeploy. Defaults from synthetic tuning.
Counter: "Who sets them in production?"
Counter-A: Bank risk team via the admin panel — that's the intended workflow; today it's DB-config only.

**Q28. Explain the event-loop bug you fixed.**
A: The Supabase client is bound to one async event loop; production restarts created a second loop → "event loop is closed". Fix: create the client inside `run()` and close it in the same loop — documented in `db.py`.

**Q29. How does the Streamlit app talk to the same DB?**
A: It imports the same adapter layer; its `run()` uses the same loop-safe pattern. The E2E test exercises both apps against live Supabase.

**Q30. What is your schema's write path?**
A: Transactions/accounts are seeded via scripts; victims insert chat rows (RLS-scoped); analysts manage cases/alerts. No public write path exists for transactions — fake-data injection is not possible from the UI (only the simulator endpoint, which is analyst-gated).

## 10.3 CYBERSECURITY (15)

**Q31. Name one vulnerability in your system.**
A: The biggest today: anonymous SELECT on chat tables means any user could read victim conversations via the REST API. It's a one-line RLS policy change to close, and it's fix #1 on our list. Saying it first is our defence.
Counter: "So it's currently vulnerable?"
Counter-A: In the strict sense yes, for chat read access. We don't run it in production with real victims until it's closed — the live demo uses synthetic data.

**Q32. How do you prevent prompt injection?**
A: System-prompt hardening, grounding, output cap, no tool access, deterministic final tier. Residual: an attacker could still elicit odd text — but not dangerous actions, because Mitra has no actions.

**Q33. What happens if your Supabase secret key leaks?**
A: Full data read/write — that's why it's gitignored, never in the browser bundle, and we rotate before final round. Leak response: revoke key, rotate, audit logs.
Counter: "How do you know it never leaked?"
Counter-A: `git log` shows no secret ever committed; we'll show that if asked.

**Q34. Rate limiting?**
A: Not implemented on chat yet — acknowledged. Planned: per-IP and per-session limits (10 msg/min), plus the LLM quota acting as a natural brake. Analysts are behind auth.
Counter: "So I can spam you right now."
Counter-A: On the public chat today, yes, within LLM quota limits. It's on the fix list before any public deployment — we won't claim otherwise.

**Q35. Is victim data PII-protected?**
A: Chat stores no names/numbers unless the victim types them; sessions are ID-based. DPDP-minimization mindset. Real deployment would add encryption at rest for message bodies — currently plaintext in Postgres (row-level access is the control).
Counter: "Encryption at rest?"
Counter-A: Not implemented; Postgres-level access control + TLS in transit today. At-rest encryption is a deployment item.

**Q36. How is analyst auth done?**
A: Supabase Auth (email/password), session JWT; admin API (secret-key) for create/reset/remove — chosen because the user-facing JWT expires in ~1h and broke password changes (we found and fixed that bug).
Counter: "MFA?"
Counter-A: Not yet — planned for the pilot. Until then, strong passwords + admin-API resets.

**Q37. What's your CORS posture?**
A: Allow-list: localhost:5173/3000 (dev) and same-origin in production (FastAPI serves the SPA). No wildcard.
Counter: "Why any localhost at all?"
Counter-A: Development convenience; production config excludes them.

**Q38. XSS via chat content?**
A: React escapes by default; Streamlit renders via `md_light()` which HTML-escapes before injecting. We pass no raw HTML from the LLM.

**Q39. Can an attacker manipulate risk scores?**
A: Scoring is read-path from DB; the only write paths are seed scripts and the analyst-gated simulator. Public APIs are read-only for transactions. Manipulation would require DB access = the secret key threat (Q33).

**Q40. DoS on the analyst dashboard?**
A: Possible via the public API today (no auth on dashboard GETs in the React app? — actually analyst routes sit behind React router, but the API endpoints themselves are open). Mitigation: hosting-level limits + auth on API (planned).
Counter: "So your KPIs are public?"
Counter-A: The API endpoints are technically open today; the UI gates access. Securing the API layer is on the fix list — honest.

**Q41. Man-in-the-middle?**
A: HTTPS on all deployed surfaces (Streamlit Cloud, Render); localhost-only in dev. No plaintext endpoints in production.

**Q42. Insider threat — an analyst abusing access?**
A: Possible — password-gated admin actions, but no audit log yet. Audit trail (who changed what) is a planned Phase-1 item; we state this openly.

**Q43. Supply chain risk?**
A: Frontend has a committed lockfile; backend requirements are listed but not pinned to hashes. We'd pin + add CI dependency scanning before pilot.

**Q44. Can the simulator endpoint be abused?**
A: It's analyst-gated in the UI; the API itself is open like other endpoints — same fix list: auth on all API routes, not just UI.

**Q45. How do you respond to a breach?**
A: Plan: revoke keys (Supabase console), stop public surface, restore from Postgres backups, document timeline. We don't have a formal incident runbook yet — that's honest; it's a deployment item, not a college-round claim.

## 10.4 INNOVATION & USP (10)

**Q46. What is genuinely novel here?**
A: Not any single component — the combination: explainable hybrid scoring + grounded victim-side RAG + cross-account fund trails + dual open frontends in one platform, with a no-login victim path. We haven't found that bundle in any single product.
Counter: "So you assembled existing pieces."
Counter-A: Correct — and that's what products are. Our contribution is the integration, the explainability layer, and the victim-first design decisions (Hinglish, no login, 1930 path).

**Q47. What stops another team from copying you in 3 weeks?**
A: Nothing structural — we're students. What's harder to copy: the tested E2E (26 tests + live-supabase lifecycle), the corpus curation (43 FAQs), the deployment hardening, and the operational knowledge (event-loop bug, JWT bug, quota fallback). That's an execution moat, not an IP moat.

**Q48. Why victim-first, when money is with the banks?**
A: Because the victim is the only party with zero tools today. Banks have Falcon; police have NCRP; the victim has a helpline they must remember to call. That unserved user is our wedge — and it feeds the analyst side with data.

**Q49. Is explainability a real advantage or a marketing line?**
A: Real. Analyst triage of "why is this flagged" is a documented pain; Falcon-style black boxes create alert fatigue. Our API returns `risk_reasons[]` and the UI shows them — measurable in the demo.

**Q50. Your Hinglish LLM — why not just English?**
A: Because target victims are low-digital-literacy users where Hindi/Hinglish comprehension is dramatically higher. The system prompt explicitly allows Hinglish empathy. It's a UX decision with a corpus to back it.

**Q51. What's your data moat?**
A: None yet — we use synthetic + public data. A pilot would create a labeled-fraud corpus and cross-bank trail knowledge; that becomes the moat. Honest: moat comes with data, not code.

**Q52. Why not use an off-the-shelf fraud API?**
A: Cost (enterprise), opacity, no victim layer, no cross-bank trails, and vendor lock-in. We're building the open alternative for pilot-scale and education/research contexts — including our own college's CEN program.

**Q53. What's the one decision that most shaped the product?**
A: One backend, two frontends — it forced every feature to be an API feature, which kept scoring, RAG, trails, and admin identical across surfaces and testable end-to-end.

**Q54. Which feature would you cut if you had to?**
A: The React app — Streamlit covers the analyst demo fully. We keep React because it's the productization path (SaaS-grade UX), but the platform's value survives without it.

**Q55. Where do you draw the line between chatbot and enforcement?**
A: Mitra guides; the analyst system enforces (block decisions, alerts, cases). We deliberately never let the LLM take actions — no false-positive damage from a hallucinated block.

## 10.5 FEASIBILITY (10)

**Q56. Can you deploy this in a bank?**
A: Not tomorrow — but the architecture is deploy-ready for a sandbox pilot: Docker single-service, managed Postgres, API design already mirrors bank integration patterns. What's missing is real data + compliance sign-off, not engineering.

**Q57. What's the cost at 1M transactions/day?**
A: Rough order: ~₹60-90k/mo (managed Postgres at scale + 2-4 app servers + LLM budget with caching/streaming). Today we pay ₹0. The scaling math is in our roadmap; the per-transaction cost is the LLM/embedding spend — grounding-only queries keep it small.

**Q58. Who will actually adopt this?**
A: Realistic path: college CEN cell as first user (operational need + local champion), then a partner bank/PSU pilot via KAVACH/SIH exposure. Banks adopt through pilot programs, not cold sales.

**Q59. Legal — can you legally process fraud complaints?**
A: Our role is detection + guidance to official channels (1930/NCRP), which are public services. We're an aggregator/assistant, not a complainant. Real deployment needs DPDP compliance review + data-sharing agreements — flagged in our roadmap.

**Q60. What if the LLM gateway is down during the demo?**
A: The demo script has a no-LLM path (investigate, fund trail, link analyzer) and a recorded video fallback. The KB tier means chat still answers — just without the ✨ AI chip.

**Q61. How long to reach pilot?**
A: Honest estimate: 6-10 weeks with a data partner — RLS hardening (1 day), rate limits (1 day), sandbox API integration (2-4 weeks), compliance review (2-4 weeks). Everything else exists.

**Q62. Do you need GPUs?**
A: No — XGBoost on CPU; embeddings via API; self-hosted STT (if added) needs only modest CPU/RAM. That's a feasibility strength.

**Q63. Who maintains it after the hackathon?**
A: The college CEN/CoE cell can operate it (students + faculty mentor); the pilot phase would be run by us under faculty supervision. Sustainability is a real question — we're proposing the CEN cell as the operational home.

**Q64. What's your disaster-recovery story?**
A: Managed Postgres (Supabase) provides backups; app is stateless (all state in DB) — redeploy from Docker in minutes. No formal DR test yet — honest.

**Q65. Is the free tier sustainable?**
A: For the college demo: yes (we've run it for weeks). For pilot: no — hence the ₹2-4k/mo pilot budget. We're clear that free tier is a demo tier, not a production tier.

## 10.6 SCALABILITY (10)

**Q66. What breaks at 10k transactions/day?**
A: Nothing structural — Postgres indexes + a queue for async scoring would smooth latency. Our scoring is fast enough that even sync would cope at this scale; the queue is for headroom.
Counter: "Queue? You don't have one."
Counter-A: Correct — the plan is to add it; today's scale doesn't need it. We're not claiming what we don't have.

**Q67. What breaks at 1M users?**
A: Postgres write throughput on `transactions`, realtime channel fan-out, and LLM cost. Fixes: time-partitioned tables, read replicas for dashboards, batch workers, grounding-only LLM budget. Standard practices — specified, not built.

**Q68. How do you scale the chat?**
A: The LLM calls are the bottleneck, not the app. Rate limits + caching (same question → same grounded answer) + streaming for perceived speed + optional self-hosted small model. Campus gateway handles demo scale only.

**Q69. Multi-tenant?**
A: Designed for multi-bank/multi-CEN use (accounts/cases carry refs; no global singletons), but tenant isolation (schema-per-tenant or tenant_id column + policies) is not implemented yet — honest.

**Q70. Can the fund trail scale?**
A: Per-query BFS over indexed edges is fine to millions of edges; deeper analytics would move to precomputed aggregate graphs. Query time grows with network size — we'd add depth caps + caching.

**Q71. Real-time at payment time?**
A: Our scoring endpoint is fast enough (sub-100ms measured) but real-time UPI interception needs the bank/NPCI sandbox API — Phase 2. Today it's near-real-time analytics, not payment-path blocking.

**Q72. CDN/static serving?**
A: FastAPI serves the SPA directly today; a CDN (or nginx) would front it at scale — trivial change, standard practice.

**Q73. How do you handle LLM latency spikes?**
A: The cooldown flag (skip LLM for 5 min after 2 failures) + template fallback keeps the victim waiting <2s worst case. Plus planned streaming.

**Q74. Observability?**
A: Logging exists (structured, per-module); no metrics dashboards/alerting yet — deployment item.

**Q75. At 1M users, what's your biggest honest unknown?**
A: Postgres write pattern under burst load and LLM economics per conversation. Both have standard answers; neither is validated by us — that's the difference between our roadmap and our evidence.

## 10.7 COMPETITORS (10)

**Q76. FICO Falcon is a decade ahead — why are you relevant?**
A: We're not competing for the same enterprise contract. We're the open, explainable, victim-inclusive layer: banks already using Falcon lack reasons, cross-bank trails, and victim guidance. We complement or replace at pilot scale.

**Q77. What does Falcon do better than you?**
A: Decades of model tuning, real transaction data, bank-native integration, regulatory trust. We say this honestly — the gap is real, and our answer is a pilot on real data, not marketing.

**Q78. Isn't 1930 + NCRP enough for victims?**
A: They're official and reactive. 1930 requires the victim to know it exists, wait on hold, and describe everything manually. Mitra sits before that: instant, guided, Hinglish, then hands off to official channels. We're an on-ramp, not a replacement.

**Q79. What about Google/Banks' built-in scam detection?**
A: They detect on the payment path (good) but don't guide the victim afterward or give analysts cross-account trails. Different layer, same problem space.

**Q80. Open-source fraud tools exist — why not use them?**
A: They're analyst-only libraries, not products: no victim layer, no UI, no RAG, no deployment. We built the product around the scoring science; the science alone doesn't serve victims.

**Q81. A big company could build this in a year.**
A: Yes — and they'd need victim-first product thinking and cross-bank data access, both of which are organizational, not technical, hurdles. Our edge today is execution speed and the college/CEN context.

**Q82. How are you different from a generic chatbot?**
A: Grounded RAG (43-FAQ corpus, verified steps), urgency-aware framing, rescue workflow (freeze → 1930 → NCRP), voice input, and it's wired to a real analyst platform — a chatbot is a feature; Mitra is a product layer.

**Q83. Positioning vs banks' in-app fraud pages?**
A: Banks' pages are static advice; Mitra is conversational, personalized to urgency/category, and backed by an analyst platform. Static content can't triage "it happened 5 minutes ago".

**Q84. If RBI builds this, you're done?**
A: Possible — and we'd be delighted, because the problem is solved. Until then, pilots like ours generate the evidence and product patterns that make such standardization possible.

**Q85. Who's your real competition in the internal round?**
A: Teams with mockups. Our working product + tests + honest gaps is the differentiation — the strongest competitor is a team with a great story and a working demo; we aim to be that team.

## 10.8 DEMO / PROTOTYPE (10)

**Q86. What's actually real in the demo vs scripted?**
A: Everything visible is live against real Supabase: chat (real LLM), scoring (real model), fund trail (real DB query), link score (real heuristic), CSV (real export). The only scripted part is the data (synthetic seed).

**Q87. Show me the model file.**
A: [Open `data/models/` + `ml/loader.py`] — 22-feature XGBoost bundle loaded at startup; logs "Models loaded: 22".

**Q88. What if the network fails mid-demo?**
A: Recorded 3-minute video is our backup, plus the demo script cuts to non-LLM steps. We rehearse the failure path.

**Q89. How long did you actually take to build this?**
A: [Honest: weeks of iterations — say your real timeline, e.g. "~6 weeks of evenings across 6 people, with several full rebuilds"]. The bugs we fixed (event loop, JWT, quota) are real development history we can narrate.

**Q90. Show me a failing case — a message Mitra gets wrong.**
A: [If you have one from testing, show it; else:] Ambiguous short messages like "money gone" classify as payment fraud by keyword — sometimes with wrong category. That's a known limit; follow-up questions re-classify. Honest limits beat fake perfection.

**Q91. Why is chat latency 2-9s?**
A: LLM gateway round-trip dominates; embeddings add ~1s; our code adds ~50-200ms. Fallback tier is <2s. Streaming is the planned fix for perceived latency.

**Q92. Can I try the analyst admin right now?**
A: Yes — create a temp analyst, reset their password, log in with it, remove them. The E2E test does exactly this live.

**Q93. How much of the React app is used daily?**
A: The Streamlit command center is our demo surface; the React app is the productization path. Both run the same API — we dogfood both in tests.

**Q94. Is the voice input actually working?**
A: Honest: transcription needs Gemini, which is currently denied — the mic shows the flow but transcribes only when Gemini works. We either add local STT before the round or demo without it. We won't fake it.
Counter: "So a headline feature is broken?"
Counter-A: It's API-gated, not design-broken; the pipeline exists and the UI works. We're choosing honesty over a fake demo, and local STT is a one-week fix.

**Q95. What's the demo's single best moment?**
A: The E2E analyst lifecycle (create → reset → remove) running live — it proves the backend is real against a real database, which mockups can't do.

## 10.9 TEAM / PROJECT (10)

**Q96. Who did what?**
A: Gaurav (backend/security), Ritik (ML), Krishna (graphs/link analysis), Prashant (RAG/LLM/voice), Satyam (React UI/deployment), Divyanshu (Streamlit CC/tests). Every member can defend the whole system (we cross-rehearse).

**Q97. What did you personally build?** (each member)
A: [Each: 2-3 concrete items + one bug you fixed. Example: "I wrote the scoring formula and the 22-feature builder; I also found that the anomaly weight barely moved the score and rebalanced it."] Specificity is credibility.

**Q98. What was your hardest bug?**
A: Candidates: event-loop closure in production; JWT expiry breaking password changes; Gemini quota killing the chat silently. Pick one and narrate root cause → diagnosis → fix → test.

**Q99. What would you redo?**
A: We'd add the queue + auth on API routes earlier, and start user interviews in week 1. Architecture first, validation second — that's the honest lesson.

**Q100. Conflict in the team?**
A: We resolved scope debates (two frontends vs one) by testing both and measuring integration cost; the API-first decision settled it. Teams that say "no conflict" sound fake.

**Q101. How did you split the 6 roles?**
A: By strength + ownership of modules; everyone cross-reviews code and rehearses Q&A outside their module.

**Q102. What's your GitHub discipline?**
A: Commits are atomic and pushed; secrets never committed (verified in history); tests run before every push. [Show repo if asked.]

**Q103. What did you learn that surprised you?**
A: Good answers: "Free-tier LLM quota is the real production risk, not model quality." / "RLS policies are the security boundary, not the API." — these show real learning.

**Q104. Why six people and not three?**
A: Six modules with real work each (backend, ML, graphs, RAG, UI, testing/deploy); every person has a shipped artifact, not a slide.

**Q105. What's the next 30 days if you win the internal round?**
A: [Concrete: RLS fix + rate limits + local STT + user interviews + load test + pilot contact list.] Specific, not "we'll improve".

## 10.10 CROSS-DEFENCE QUESTIONS (12) — for members outside their section

**Q106. (to Prashant, problem guy) "How does your backend prevent SQL injection?"**
A: No raw SQL on the API — the Supabase adapter parameterizes all queries; DB access is REST + RLS. If injection details are needed, Gaurav: [pass]. (Rule: answer, then delegate.)

**Q107. (to Ritik, landscape guy) "Your chatbot gives rescue steps — who verifies those steps are correct?"**
A: They're curated in the corpus (seeded from RBI/1930/NCRP guidance), reviewed by the team; the LLM can't invent new steps because of grounding + cap. Prashant owns corpus versioning.

**Q108. (to Divyanshu, solution guy) "Where does the risk score come from?"**
A: FastAPI → ML bundle (XGBoost + rules) → stored in the transaction row; the UI just renders `risk_score` + `risk_reasons`. Ritik can deep-dive.

**Q109. (to Satyam, architect) "Your chat is public and anonymous — how do you stop abuse?"**
A: Rate limits are planned (per-IP/per-session); the LLM quota is a natural brake; RLS-scoped inserts only; audit of abuse cases is on the roadmap. Gaurav owns the security details.

**Q110. (to Gaurav, security guy) "What's the user journey for a victim?"**
A: Open chat (no login) → type/speak → classification + urgency → grounded rescue steps → 1930 tap. Divyanshu and Prashant can walk the product flow.

**Q111. (to Krishna, demo guy) "Why two frontends instead of one?"**
A: One backend, two audiences: analysts want speed (Streamlit), banks want product-grade UX (React). The API-first rule keeps them equivalent. Satyam owns deployment.

**Q112. (to Prashant) "What's your ML accuracy?"**
A: On synthetic hold-out we can show confusion matrix/ROC; real accuracy needs real data — we state that boundary. Ritik has the numbers.

**Q113. (to Ritik) "How do victims reach your app?"**
A: Today a web URL (public chat, no install); Phase 4: WhatsApp bot + app. Distribution is the growth problem we've planned, not yet built.

**Q114. (to Divyanshu) "What stops me from deleting all cases?"**
A: Cases API is write-capable only through analyst workflows; admin actions are password-gated; audit logging is planned. Database backups via managed Postgres.

**Q115. (to Satyam) "How is the demo data generated?"**
A: `generate_synthetic.py` encodes fraud patterns (bursts, mules, night transfers); seeded via `seed_data.py`; 127 transactions, 5 flagged — synthetic by design, labelled as such.

**Q116. (to Gaurav) "What's your biggest remaining risk?"**
A: Three, in order: real-data validation (does scoring hold on real fraud?), victim privacy (RLS gap — being fixed), and LLM independence (campus gateway is a crutch). We say these in the presentation.

**Q117. (to Krishna) "Can the fund trail be faked by an attacker?"**
A: It reads only seeded/validated transactions; no public write path; simulator is analyst-gated. Same threat model as scoring integrity.

---

# PART 11 — RED-TEAM REVIEW (strict judge tries to reject us)

| # | Weakness | Why the judge will attack it | How we fix it (before/at the round) |
|---|---|---|---|
| R1 | Synthetic data only | "Your model has never seen real fraud" | Label everything synthetic; bring confusion matrix; make the pilot ask the centerpiece; never claim real-world accuracy |
| R2 | RLS anon SELECT on chats | Privacy violation on a fraud platform | Fix the policy BEFORE the round (one-line SQL, re-test E2E); screenshot the new policy; say it on slide 11 |
| R3 | Voice STT broken | Headline feature that fails | Implement local STT (faster-whisper small, ~1GB, offline) OR drop voice from demo with honest statement; do not fake |
| R4 | Campus LLM gateway | Not a real deployment LLM; shared/slow | Present as zero-cost pilot choice; show config-swap design; name hosted fallback in roadmap |
| R5 | No rate limiting on public chat | Abuse/cost | Add simple per-IP limit (1 day of work) + mention LLM quota as natural brake |
| R6 | API endpoints not auth-gated | Anyone can hit dashboards | Add API-key gate for analyst routes (small middleware) or state clearly that UI-only gating is a demo-stage choice being fixed |
| R7 | No user interviews | "Victims need this" is unproven | Do 5-10 quick interviews before round; even a mini survey of seniors/campus = evidence |
| R8 | Unverified stats (₹1,453 Cr) | Fabricated numbers destroy credibility | Source the stat on the slide with year + report; otherwise remove |
| R9 | "Scalable to 1M" with no load test | Standard student overclaim | Run a quick load test (locust/ab, 200 concurrent) and show honest numbers; phrase scale claims as roadmap with bottlenecks named |
| R10 | Two frontends seen as waste | "Why not one?" | Defend as two audiences + API-first discipline; show the shared-router diagram |
| R11 | No MFA / no audit log | Security maturity gap | Say it as planned Phase-1 items with exact timeline; never claim them |
| R12 | Simulator can inject data | Data integrity | Keep analyst-gated; state write-path restrictions (R30/44 answers) |
| R13 | Demo depends on internet + gateway | Network failure kills pitch | Pre-recorded 3-min video + no-LLM demo path + rehearsed failure handling |
| R14 | Team = 6 students, no mentor ops plan | Sustainability doubt | Propose CEN cell as operational home; name faculty mentor; show handover docs (scripts/tests) |
| R15 | XGBoost on synthetic = arbitrary weights | "Why 0.6/0.1/0.3?" | Show tuning notebook/grid search; commit to re-tuning on real data in pilot |
| R16 | Chat history readable by anon (see R2) | DPDP violation | Same fix as R2; mention DPDP minimization posture |
| R17 | No incident response runbook | "What if you're breached?" | Have a written 1-page runbook (revoke keys, restore from backup, notify) — even a simple one |
| R18 | React app may look unused | "Is this abandoned?" | Show both apps in demo; dogfood React in testing; say it's the productization path |

---

# PART 12 — FINAL SCORE

## 12.1 Rubric scoring (strict)

| Category | Weight | Current | After fixes | Notes |
|---|---|---|---|---|
| Problem Understanding & Impact | /20 | 15 | 17 | Strong problem, weak evidence (stats + interviews) |
| Innovation & Differentiation | /20 | 14 | 16 | Integration USP real; components individually exist |
| Technical Excellence | /25 | 17 | 20 | Real build + tests; gaps: auth-on-API, rate limits, voice, queue |
| Validation, Feasibility & Scalability | /20 | 11 | 15 | Tests good; synthetic-data + no load test + no interviews hurt |
| Solution Quality, UX & Presentation | /15 | 11 | 13 | Premium UI + working demo; rehearsal + backup video needed |
| **TOTAL** | **/100** | **68** | **81** | — |

## 12.2 Top 5 changes that increase the score the most
1. **Fix RLS + rate limits + API auth gate** (technical excellence + security: ≈ +4-5) — one day of work, screenshottable.
2. **Evidence pack** — latency table, retrieval table, confusion matrix, source citations (validation: ≈ +3).
3. **Real user interviews (5-10)** with honest quotes (impact + validation: ≈ +2-3).
4. **Local STT or honest voice story** (technical + demo: ≈ +2).
5. **Load test + scaled claims with named bottlenecks** (feasibility: ≈ +2).

## 12.3 Final verdict
At 68/100 this is a **strong college prototype with honest framing issues**. The gap to 81 is not more features — it's **security hardening, evidence collection, and honest claim discipline**. The judges' #1 rejection reason would be "synthetic data + campus gateway + unsecured chat" — all three are addressable before the round. The #1 reason they'd advance you is the **working E2E system with a real demo** — which you already have.

**Do tomorrow (in order):**
1. RLS fix + re-run E2E
2. Rate limit on chat (per-IP)
3. Source the two statistics or remove them
4. Record the 3-min backup demo video
5. Rehearse Q&A with the 12 cross-defence questions — every member answers all