-- Prototype-only public room storage. Not production-safe: clients can read or alter room state.
create table if not exists public.football_bowls_rooms (
  code text primary key,
  state jsonb not null,
  version integer not null default 0,
  created_at timestamptz not null default now()
);
alter table public.football_bowls_rooms enable row level security;
create policy "demo room read" on public.football_bowls_rooms for select to anon using (true);
create policy "demo room create" on public.football_bowls_rooms for insert to anon with check (true);
create policy "demo room update" on public.football_bowls_rooms for update to anon using (true) with check (true);
-- Schedule deletion of old rooms before production deployment.
