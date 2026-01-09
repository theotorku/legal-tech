-- Run this in Supabase SQL editor to create the `contracts` table
-- Updated schema for production-ready contract analyzer

create table if not exists public.contracts (
  id uuid default gen_random_uuid() primary key,
  filename text not null,
  pages integer default 1,
  file_size integer,
  content_type text,
  contract_type text,
  parties jsonb,
  key_dates jsonb,
  key_terms jsonb,
  risk_level text,
  summary text,
  analysis jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Indexes for performance
create index if not exists idx_contracts_created_at on public.contracts(created_at desc);
create index if not exists idx_contracts_contract_type on public.contracts(contract_type);
create index if not exists idx_contracts_risk_level on public.contracts(risk_level);

-- Enable Row Level Security (RLS)
alter table public.contracts enable row level security;

-- Create policy for authenticated users (adjust as needed)
create policy "Enable read access for all users" on public.contracts
  for select using (true);

create policy "Enable insert access for all users" on public.contracts
  for insert with check (true);

-- Function to update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Trigger to automatically update updated_at
create trigger set_updated_at
  before update on public.contracts
  for each row
  execute function public.handle_updated_at();
