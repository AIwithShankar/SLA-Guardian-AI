# SLA Guardian AI

Phase 2 project foundation for a B2B customer-support SLA breach prediction application.
Phase 3 now contains provisional research documentation and Colab dataset artifacts.
No production model, database workflow, authentication, or prediction service is
implemented.

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
├── notebooks/
├── data/processed/ (ignored provisional research artifacts)
├── supabase/migrations/
├── docs/{PRD.md,architecture.md,data-contract.md,phase3/}
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

## Phase 3 progress

The Colab notebook at
[notebooks/03_dataset_discovery_eda.ipynb](./notebooks/03_dataset_discovery_eda.ipynb)
and the provisional manifest at
`data/processed/dataset_manifest.json` document dataset discovery, conservative
cohort construction, provisional SLA labels, chronological splits, and
outcome-maturity audits.

Read the Phase 3 documentation:

- [Data quality report](./docs/phase3/data_quality_report.md)
- [Feature dictionary](./docs/phase3/feature_dictionary.md)
- [SLA label definition](./docs/phase3/sla_label_definition.md)
- [Split strategy](./docs/phase3/split_strategy.md)

These are research assumptions only. No model was trained, no model results are
claimed, and `data/raw/`, `data/processed/`, and `data/artifacts/` are excluded
from Git.
