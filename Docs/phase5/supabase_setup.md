# Phase 5B.1 Supabase setup

Phase 5B.1 provides the database and authentication foundation. Phase 5B.2
adds the authenticated prediction route; it remains research-only and
nonpersistent.

## Required user actions

1. Create a dedicated Supabase test project. Do not use production credentials
   for integration tests.
2. In the Supabase SQL Editor for that test project, apply:
   `supabase/migrations/20261117190000_phase5b1_foundation.sql`.
3. Create test users through Supabase Auth.
4. Insert corresponding `public.organizations` and `public.profiles` rows using
   the Supabase SQL Editor or a protected administrative workflow. Authenticated
   clients have no profile write privileges. The profile
   `user_id` must equal the Auth user UUID. Do not accept organization or role
   values from a client.
5. Add test SLA policies and tickets with UTC timestamps. Each prediction
fixture ticket must have a valid `sla_policy_id` foreign key and a stored
future `sla_deadline`; the API rejects tickets without both values.
6. Keep the Supabase anon key in backend environment configuration only for now.
   Never place a service-role key in React or commit either key.

## Environment variables

Set these in a local, ignored `.env` file:

```text
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=YOUR_PUBLIC_ANON_KEY
```

`SUPABASE_KEY` is accepted as a backward-compatible alias by the backend
settings, but `SUPABASE_ANON_KEY` is the documented name. No credential value
belongs in Git.

## Local commands

From the repository root:

```powershell
Copy-Item .env.example .env
notepad .env

Set-Location backend
& .\.venv\Scripts\python.exe -m pytest tests\test_supabase_foundation.py -q
```

The unit tests use mocked HTTP clients and do not contact Supabase.

## Separate cloud integration procedure

Use a dedicated Supabase test project and test-only Auth users. After applying
the migration and inserting test fixtures, run authenticated HTTP checks with
the test users:

1. `GET /auth/v1/user` with the user's bearer token and anon key returns the
   authenticated user.
2. A profile lookup returns only that user's trusted profile.
3. A manager can read tickets in their organization.
4. An agent can read only assigned tickets.
5. A user from organization A cannot read organization B tickets.
6. An invalid or expired token is rejected.
7. Direct PostgREST access with a mismatched organization filter returns no
   cross-tenant rows because RLS remains enabled.

Those checks require real project URL, anon key, Auth users, and fixture UUIDs.
They have not been executed in this workspace and no Supabase integration result
is claimed.
