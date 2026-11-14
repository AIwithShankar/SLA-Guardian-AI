# SLA Guardian AI

Lightweight scaffolding for a machine learning system that predicts customer support ticket SLA breaches.

## Project structure

```text
SLA-Guardian-AI/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── .env.example
├── .env.example
└── README.md
```

The backend currently runs in mock mode when Supabase credentials and a trained model are unavailable. The ML, database, and service boundaries are ready for later implementation.

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Run the backend (Windows PowerShell)

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://127.0.0.1:8000`. OpenAPI docs are at `http://127.0.0.1:8000/docs`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal and activate again.

## Run the frontend

In a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`. The dashboard calls `GET /api/v1/health` and displays mock ticket data from the backend.

## API endpoints

- `GET /api/v1/health` - service health and mock-mode status
- `GET /api/v1/tickets` - mock ticket list
- `POST /api/v1/predictions` - placeholder prediction response

No API keys or credentials are committed. Copy `.env.example` and fill in Supabase values only when database integration is ready.
