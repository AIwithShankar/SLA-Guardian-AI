-- Phase 5B.1 foundation for Supabase Auth, tenant isolation, and tickets.
-- Apply this migration only to a dedicated Supabase project first.

create extension if not exists pgcrypto;

create table if not exists public.organizations (
    id uuid primary key default gen_random_uuid(),
    name text not null check (length(trim(name)) between 1 and 200),
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    organization_id uuid not null references public.organizations(id) on delete restrict,
    role text not null check (role in ('agent', 'manager', 'admin')),
    display_name text not null check (length(trim(display_name)) between 1 and 200)
);

create table if not exists public.sla_policies (
    id uuid primary key default gen_random_uuid(),
    organization_id uuid not null references public.organizations(id) on delete cascade,
    priority text not null check (priority in ('critical', 'high', 'medium', 'low')),
    target_minutes integer not null check (target_minutes > 0),
    version integer not null check (version > 0),
    created_at timestamptz not null default timezone('utc', now()),
    unique (organization_id, priority, version)
);

create table if not exists public.tickets (
    id uuid primary key default gen_random_uuid(),
    organization_id uuid not null references public.organizations(id) on delete cascade,
    external_ticket_id text not null check (length(trim(external_ticket_id)) between 1 and 200),
    assigned_agent_id uuid references public.profiles(user_id) on delete set null,
    priority text not null check (priority in ('critical', 'high', 'medium', 'low')),
    status text not null check (status in ('open', 'in_progress', 'resolved')),
    category text not null default 'Unknown',
    created_at timestamptz not null,
    resolved_at timestamptz,
    last_updated_at timestamptz,
    sla_policy_id uuid references public.sla_policies(id) on delete restrict,
    sla_deadline timestamptz,
    unique (organization_id, external_ticket_id)
);

create index if not exists profiles_organization_id_idx
    on public.profiles (organization_id);
create index if not exists sla_policies_organization_priority_idx
    on public.sla_policies (organization_id, priority, version desc);
create index if not exists tickets_organization_status_idx
    on public.tickets (organization_id, status);
create index if not exists tickets_organization_assignee_idx
    on public.tickets (organization_id, assigned_agent_id);
create index if not exists tickets_organization_created_idx
    on public.tickets (organization_id, created_at desc);

create or replace function public.current_profile_organization()
returns uuid
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
    select organization_id
    from public.profiles
    where user_id = auth.uid()
$$;

create or replace function public.current_profile_role()
returns text
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
    select role
    from public.profiles
    where user_id = auth.uid()
$$;

revoke execute on function public.current_profile_organization() from public;
revoke execute on function public.current_profile_role() from public;
grant execute on function public.current_profile_organization() to authenticated;
grant execute on function public.current_profile_role() to authenticated;

alter table public.organizations enable row level security;
alter table public.profiles enable row level security;
alter table public.sla_policies enable row level security;
alter table public.tickets enable row level security;

drop policy if exists organizations_member_select on public.organizations;
create policy organizations_member_select
on public.organizations for select to authenticated
using (id = public.current_profile_organization());

drop policy if exists profiles_self_select on public.profiles;
create policy profiles_self_select
on public.profiles for select to authenticated
using (user_id = auth.uid());

drop policy if exists profiles_admin_manage on public.profiles;

drop policy if exists sla_policies_member_select on public.sla_policies;
create policy sla_policies_member_select
on public.sla_policies for select to authenticated
using (organization_id = public.current_profile_organization());

drop policy if exists sla_policies_admin_write on public.sla_policies;
create policy sla_policies_admin_write
on public.sla_policies for all to authenticated
using (
    organization_id = public.current_profile_organization()
    and public.current_profile_role() = 'admin'
)
with check (
    organization_id = public.current_profile_organization()
    and public.current_profile_role() = 'admin'
);

drop policy if exists tickets_member_select on public.tickets;
create policy tickets_member_select
on public.tickets for select to authenticated
using (
    organization_id = public.current_profile_organization()
    and (
        public.current_profile_role() in ('manager', 'admin')
        or assigned_agent_id = auth.uid()
    )
);

drop policy if exists tickets_manager_admin_write on public.tickets;
create policy tickets_manager_admin_write
on public.tickets for all to authenticated
using (
    organization_id = public.current_profile_organization()
    and public.current_profile_role() in ('manager', 'admin')
)
with check (
    organization_id = public.current_profile_organization()
    and public.current_profile_role() in ('manager', 'admin')
);

revoke all on public.organizations, public.profiles,
    public.sla_policies, public.tickets from anon;
grant select on public.organizations, public.profiles,
    public.sla_policies, public.tickets to authenticated;
grant insert, update, delete on public.sla_policies, public.tickets
    to authenticated;
