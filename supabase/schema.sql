-- Amaru Collections — waitlist table
-- Run once in Supabase: Dashboard → SQL Editor → paste → Run.

create table if not exists public.waitlist (
  id          uuid primary key default gen_random_uuid(),
  email       text not null check (char_length(email) between 3 and 320 and email ~* '^[^\s@]+@[^\s@]+\.[^\s@]+$'),
  name        text check (name is null or char_length(name) <= 120),
  locale      text not null default 'en' check (char_length(locale) <= 8),
  source      text check (source is null or char_length(source) <= 40),
  created_at  timestamptz not null default now()
);

-- One sign-up per address, case-insensitive. Duplicate inserts return 409,
-- which the site treats as success.
create unique index if not exists waitlist_email_lower_key on public.waitlist (lower(email));

-- Visitors can add themselves but can never read, change or delete the list.
alter table public.waitlist enable row level security;

drop policy if exists "Anyone can join the waitlist" on public.waitlist;
create policy "Anyone can join the waitlist"
  on public.waitlist for insert
  to anon
  with check (true);

grant insert on public.waitlist to anon;
