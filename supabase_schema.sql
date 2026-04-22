-- Run this in the Supabase SQL editor

create table if not exists users (
  discord_id  text primary key,
  username    text not null,
  total_score integer not null default 0,
  games_played integer not null default 0,
  games_won    integer not null default 0,
  created_at  timestamptz not null default now()
);

create table if not exists games (
  id             uuid primary key default gen_random_uuid(),
  discord_id     text not null references users(discord_id) on delete cascade,
  card_name      text not null,
  card_data      jsonb not null,
  hints_revealed integer not null default 0,
  status         text not null default 'active',  -- active | won | lost
  created_at     timestamptz not null default now()
);

-- Only one active game per user
create unique index if not exists games_one_active_per_user
  on games (discord_id)
  where status = 'active';
