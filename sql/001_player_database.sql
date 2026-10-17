-- Run in Supabase SQL Editor. Does not modify football_bowls_rooms.
create table if not exists public.fb_clubs (
  club_id text primary key,
  name text not null unique
);
create table if not exists public.fb_players (
  player_id text primary key,
  name text not null,
  wikipedia_url text,
  premier_league_id text
);
create table if not exists public.fb_player_club_appearances (
  player_id text not null references public.fb_players(player_id),
  club_id text not null references public.fb_clubs(club_id),
  appearances integer not null check (appearances > 0),
  source_url text not null,
  verified_at timestamptz not null,
  updated_at timestamptz not null default now(),
  primary key (player_id, club_id)
);
create table if not exists public.fb_data_updates (
  id bigint generated always as identity primary key,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null check (status in ('started','completed','failed')),
  details jsonb
);
alter table public.fb_clubs enable row level security;
alter table public.fb_players enable row level security;
alter table public.fb_player_club_appearances enable row level security;
alter table public.fb_data_updates enable row level security;
-- Public read access to verified game data only; writes are intentionally not granted.
drop policy if exists fb_clubs_read on public.fb_clubs;
create policy fb_clubs_read on public.fb_clubs for select to anon, authenticated using (true);
drop policy if exists fb_players_read on public.fb_players;
create policy fb_players_read on public.fb_players for select to anon, authenticated using (true);
drop policy if exists fb_appearances_read on public.fb_player_club_appearances;
create policy fb_appearances_read on public.fb_player_club_appearances for select to anon, authenticated using (true);
-- No public policies on fb_data_updates.
