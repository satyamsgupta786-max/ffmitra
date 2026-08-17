create extension if not exists vector with schema extensions;

create table if not exists public.accounts (
    id bigserial primary key,
    account_ref text unique not null,
    account_type text default 'UPI',
    holder_name text default 'UNKNOWN',
    bank text default 'UNKNOWN',
    risk_score numeric(6,2) default 0,
    txn_count bigint default 0,
    flagged boolean default false,
    created_at timestamptz default now()
);

create table if not exists public.transactions (
    id bigserial primary key,
    txn_ref text unique not null,
    source_ref text not null,
    dest_ref text not null,
    amount numeric(14,2) not null,
    currency text default 'INR',
    channel text default 'UPI',
    txn_type text default 'P2P',
    txn_time timestamptz not null,
    device_id text,
    ip_address text,
    location text,
    merchant text,
    risk_score numeric(6,2) default 0,
    risk_decision text default 'APPROVE',
    risk_reasons jsonb default '[]',
    is_fraud boolean default false,
    is_reviewed boolean default false,
    meta jsonb default '{}',
    created_at timestamptz default now()
);

create table if not exists public.flagged_accounts (
    id bigserial primary key,
    account_ref text unique not null,
    reason text default '',
    severity text default 'HIGH',
    source text default 'MANUAL',
    flagged_by text default 'system',
    active boolean default true,
    created_at timestamptz default now()
);

create table if not exists public.alerts (
    id bigserial primary key,
    txn_ref text,
    alert_type text not null,
    severity text default 'MEDIUM',
    title text not null,
    description text default '',
    account_ref text,
    acknowledged boolean default false,
    acknowledged_by text,
    created_at timestamptz default now()
);

create table if not exists public.cases (
    id bigserial primary key,
    case_no text unique not null,
    title text not null,
    category text not null,
    status text default 'OPEN',
    summary text default '',
    victim_name text,
    victim_contact text,
    source text default 'MANUAL',
    created_by text default 'system',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists public.case_notes (
    id bigserial primary key,
    case_id bigint not null references public.cases(id) on delete cascade,
    note text not null,
    author text default 'system',
    created_at timestamptz default now()
);

create table if not exists public.chat_sessions (
    id bigserial primary key,
    session_ref text unique not null,
    category text,
    status text default 'OPEN',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists public.chat_messages (
    id bigserial primary key,
    session_id bigint not null references public.chat_sessions(id) on delete cascade,
    role text not null,
    content text not null,
    created_at timestamptz default now()
);

create table if not exists public.faq_docs (
    id bigserial primary key,
    category text not null,
    question text not null,
    answer text not null,
    keywords text default '',
    embedding vector(768)
);

create table if not exists public.settings (
    key text primary key,
    value jsonb not null
);

create index if not exists idx_txns_time on public.transactions (txn_time desc);
create index if not exists idx_txns_source on public.transactions (source_ref);
create index if not exists idx_txns_dest on public.transactions (dest_ref);
create index if not exists idx_txns_ref on public.transactions (txn_ref);

DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE public.transactions; EXCEPTION WHEN others THEN null; END $$;
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE public.alerts; EXCEPTION WHEN others THEN null; END $$;
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE public.flagged_accounts; EXCEPTION WHEN others THEN null; END $$;

alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;

DO $$ BEGIN create policy "anon can insert chat_sessions" on public.chat_sessions for insert to anon with check (true); EXCEPTION WHEN duplicate_object THEN null; END $$;
DO $$ BEGIN create policy "anon can select chat_sessions" on public.chat_sessions for select to anon using (true); EXCEPTION WHEN duplicate_object THEN null; END $$;
DO $$ BEGIN create policy "anon can insert chat_messages" on public.chat_messages for insert to anon with check (true); EXCEPTION WHEN duplicate_object THEN null; END $$;
DO $$ BEGIN create policy "anon can select chat_messages" on public.chat_messages for select to anon using (true); EXCEPTION WHEN duplicate_object THEN null; END $$;

insert into public.settings (key, value) values ('thresholds', '{"review":0.6,"block":0.85,"ml_weight":0.6,"anomaly_weight":0.1,"rule_weight":0.3}') on conflict (key) do nothing;