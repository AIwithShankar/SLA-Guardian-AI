# SLA Guardian AI

Phase 2 project foundation for a B2B customer-support SLA breach prediction application.
This phase intentionally contains no database, authentication, CSV ingestion, SLA
calculation, model training, or prediction implementation.

## Project structure

```text
SLA-Guardian-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── pages/
│   ├── package.json
│   └── .env.example
├── ml/{notebooks,artifacts}/
├── supabase/migrations/
├── docs/{PRD.md,architecture.md,data-contract.md}
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Run the backend (Windows PowerShell)

From the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`. OpenAPI docs are at `http://127.0.0.1:8000/docs`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal and activate again.

Run the smoke test from the project root:

```powershell
python -m pytest backend\tests -q
```

## Run the frontend

In a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`. The dashboard calls
`GET http://127.0.0.1:8000/health` and displays the connection status.

## API endpoints

- `GET /health` - foundation service health

No API keys or credentials are committed. Database and model configuration will be
added in later phases.
