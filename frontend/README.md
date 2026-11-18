# SLA Guardian AI — Phase 6 frontend

Minimal, light, operational UI. React + Vite + Tailwind v4 + Recharts + Supabase.

## Windows PowerShell setup

From `D:\Desktop\SLA-Guardian-AI`:

```powershell
# Copy the contents of this extracted folder into your repository's `frontend` directory.
cd .\frontend
Copy-Item .env.example .env.local
notepad .env.local
npm install
npm run dev
```

Set these in `.env.local`:
- `VITE_SUPABASE_URL`: Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY`: **publishable** key, not service-role or secret key
- `VITE_API_BASE_URL`: `http://127.0.0.1:8000`

Run the backend **in another terminal** from `backend` with backend-only `SUPABASE_URL` and `SUPABASE_ANON_KEY` configured:

```powershell
.\.venv-ml\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://localhost:5173. The existing backend `FRONTEND_ORIGIN` normally defaults to this value. If you see a CORS error, check the frontend browser origin and backend `FRONTEND_ORIGIN`, then restart the backend while preserving strict CORS.

## Required existing Supabase schema

- `profiles`: `user_id`, `organization_id`, `role`, `display_name`.
- `tickets`: `id`, `external_ticket_id`, `organization_id`, `priority`, `category`, `status`, `created_at`, `sla_deadline`, `sla_policy_id`.
- RLS must let each user read their own profile and permitted tickets.
- FastAPI `POST /api/v1/tickets/{ticket_id}/predict` must accept Supabase JWT and return a research-only prediction.

## Verification

1. `npm run build` — compile.
2. Login as Manager A; see only Organization A tickets; make prediction on an open ticket with assigned SLA and future deadline.
3. Login as Agent A; prediction actions disabled.
4. Login as Admin B; cannot view Organization A's ticket in dashboard.
5. Sign out; confirm login screen.

`Tickets in view` and related counts are based on **up to 100 recent visible rows**, not full organizational totals. Risk estimates are **not persisted**. This is a research prototype, not a production security audit or alerting solution.
