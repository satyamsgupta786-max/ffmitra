-- FFMitra RLS hardening:
-- 1) Victim chat tables: NO anonymous access at all (apps talk via the
--    FastAPI service role, which bypasses RLS). Closes the victim-privacy gap.
-- 2) Realtime-fed tables (transactions, flagged_accounts, alerts): enable RLS
--    with SELECT-only anon policies — keeps the dashboard LiveFeed working
--    while closing anonymous WRITE access (prevents fake-data injection).
-- 3) Analyst-only tables (accounts, cases, case_notes, faq_docs, settings):
--    enable RLS with no anon policies.

-- 1. Chat privacy
drop policy if exists "anon can select chat_sessions" on public.chat_sessions;
drop policy if exists "anon can insert chat_sessions" on public.chat_sessions;
drop policy if exists "anon can select chat_messages" on public.chat_messages;
drop policy if exists "anon can insert chat_messages" on public.chat_messages;

-- 2. Realtime tables: RLS on, anonymous read-only (LiveFeed)
alter table public.transactions enable row level security;
alter table public.flagged_accounts enable row level security;
alter table public.alerts enable row level security;

do $$ begin
    create policy "anon can select transactions" on public.transactions
        for select to anon using (true);
exception when duplicate_object then null; end $$;
do $$ begin
    create policy "anon can select flagged_accounts" on public.flagged_accounts
        for select to anon using (true);
exception when duplicate_object then null; end $$;
do $$ begin
    create policy "anon can select alerts" on public.alerts
        for select to anon using (true);
exception when duplicate_object then null; end $$;

-- 3. Analyst-only tables: RLS on, no anonymous access
alter table public.accounts enable row level security;
alter table public.cases enable row level security;
alter table public.case_notes enable row level security;
alter table public.faq_docs enable row level security;
alter table public.settings enable row level security;