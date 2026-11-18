# SLA Guardian AI

# Phase 1 Progress

Phase 1 — Product Requirements & System Architecture

Established the product requirements and technical architecture for SLA Guardian AI, a B2B customer-support platform that estimates the probability of support tickets breaching their resolution Service Level Agreements (SLAs).

Project Objectives

Identify support tickets at risk of missing resolution deadlines.

Provide managers with early, actionable risk information.

Help support teams prioritize tickets requiring attention.

Ensure organization-level data isolation and role-based access.

Present ML predictions through a clear, intuitive dashboard.

Technology Architecture

Layer

Technology

Frontend

React, Vite, Tailwind CSS, Recharts

Backend

Python, FastAPI

Machine Learning

LightGBM, scikit-learn

Database

Supabase PostgreSQL

Authentication

Supabase Auth

Security

Row Level Security (RLS), JWT authentication

Model Training

Google Colab

Version Control

Git and GitHub

Architecture Principles

Modular separation between frontend, backend, database, and ML inference.

Tenant-scoped database access to isolate organizations.

Role-based permissions for Admin, Manager, and Agent users.

Lightweight backend inference without local model training.

Environment-based configuration without hardcoded credentials.

Research-only predictions with clear limitations.

# Phase 2 Progress

Phase 2 project foundation for a B2B customer-support SLA breach prediction application.
Phase 3 now contains provisional research documentation and Colab dataset artifacts.
No production model, database workflow, authentication, or public prediction
endpoint is implemented.

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

## Phase 4 — Machine Learning Model

Developed a research-stage SLA breach prediction model using LightGBM.

### Features

The model uses six ticket features:

- Priority
- Category
- Ticket age in hours
- Remaining SLA time in hours
- Ticket creation hour
- Ticket creation weekday

### Model Development

- Model training and experimentation using Google Colab.
- Tabular classification using LightGBM.
- Sigmoid probability calibration.
- Risk classification based on predicted breach probability.
- Reproducible inference using a versioned model artifact.
- No future-derived ticket features used during inference.

### Research Evaluation

| Metric | Reported Result |
|---|---|
| Test ROC-AUC | ~0.783 |
| PR-AUC | ~0.636 |
| High-risk threshold | 0.70 |
| High-risk precision | ~72% |
| High-risk recall | ~6.47% |
| Model version | phase4_research_v1 |

These are research evaluation results, not production performance
guarantees. In particular, recall at the high-risk threshold is low.

# Phase 5 — FastAPI, Supabase & ML Integration

Integrated the research LightGBM model into a secure, authenticated backend using FastAPI and Supabase PostgreSQL.

## Phase 5A — Trusted ML Inference

Implemented trusted loading of the versioned LightGBM model artifact.

Added model integrity verification and feature-contract validation.

Built a prediction service that constructs six inference features.

Added SLA eligibility checks and probability-based risk classification.

Implemented automated tests for model inference and prediction behavior.

## Phase 5B — Prediction Service

Implemented ticket retrieval and SLA assessment logic.

Added organization and role authorization checks.

Integrated the trained ML predictor with the FastAPI service layer.

Returned structured prediction responses containing probability, risk band, model version, deadline, and prediction status.

### Phase 5B.1 — Supabase Foundation

Created PostgreSQL tables for organizations, profiles, SLA policies, and tickets.

Implemented organization-scoped Row Level Security policies.

Connected Supabase authentication with trusted user profiles.

Configured Admin, Manager, and Agent roles.

Tested tenant separation and database access restrictions.

### Phase 5B.2 — Authenticated Prediction API

Implemented:

POST /api/v1/tickets/{ticket_id}/predict

The endpoint:

Validates the Supabase bearer token.

Retrieves the authenticated user's trusted organization and role.

Fetches the requested ticket using tenant-scoped access.

Checks authorization and SLA eligibility.

Constructs the required ML features.

Executes LightGBM inference.

Returns the prediction result to the frontend.

Integration Verification

Successfully generated a real authenticated SLA breach prediction.

Verified Manager access to the prediction endpoint.

Verified Agent requests were rejected with HTTP 403.

Verified cross-organization ticket access was rejected with HTTP 404.

Confirmed that predictions are research-only and are not persisted to the database.

Example Prediction Response

The API returns the following fields:

ticket_id

model_version

prediction_timestamp

sla_deadline

breach_probability

risk_band

prediction_status

research_only

sla_breached

No automated ticket updates, alerts, or notifications are currently implemented.

## Phase 6 — React Frontend Dashboard

Built a responsive SaaS-style dashboard using React, Vite,
Tailwind CSS, and Recharts.

### Implemented Features

- Supabase email/password authentication.
- User session restoration and logout.
- Organization-scoped ticket monitoring.
- Ticket searching and filtering.
- Ticket priority, status, and SLA deadline visibility.
- Role-aware prediction controls.
- Authenticated FastAPI prediction requests.
- SLA breach probability and risk classification.
- Readable ticket references.
- Mobile-responsive navigation and account controls.
- Research-only prediction disclaimer.

### UI Design

The interface follows a minimal, professional B2B SaaS design:

- Light theme with neutral colors.
- Clear typography and navigation.
- Simple tables and meaningful risk indicators.
- Minimal decoration and unnecessary animation.
- Accessible information hierarchy for first-time users.

### Frontend Integration

React communicates with Supabase for authentication and authorized
ticket retrieval. Prediction requests are sent to FastAPI using
the authenticated user's access token.

The FastAPI backend handles authorization, ticket eligibility,
feature construction, and LightGBM inference.

## Phase 7 — Testing and Bug Fixes

Performed backend automated testing, real integration verification,
frontend testing, and responsive UI fixes.

### Backend Testing

- 41 automated backend tests passed.
- Prediction route authorization tests passed.
- SLA eligibility handling verified.
- Model inference tests passed.
- Tenant-scoped ticket access tested.

### Real Integration Verification

- Manager A successfully authenticated and generated a prediction.
- Agent A prediction request was rejected with HTTP 403.
- Admin B could not access an Organization A ticket (HTTP 404).
- React successfully displayed real FastAPI prediction results.

### Frontend Verification

- Login and logout tested.
- Session restoration tested.
- Role-based UI behavior checked.
- Ticket dashboard and prediction flow tested.
- Responsive navigation reviewed and improved.
- Mobile profile and sign-out visibility fixed.
- Frontend production build passed.
- Production-dependency audit reported zero known vulnerabilities.

### Limitations

- The ML model is research-only.
- Predictions are advisory and not persisted.
- Automated alerts and external notifications are not implemented.
- Results have not been validated on live production workloads.
- Deployment and production monitoring remain pending.
