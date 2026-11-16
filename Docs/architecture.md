# Architecture

Phase 2 uses a lightweight modular monolith:

- React + Vite + Tailwind CSS frontend
- FastAPI + Pydantic backend
- CORS for local frontend development
- Managed services and machine learning are intentionally deferred

The browser calls `GET /health` to show backend connectivity. Database, authentication,
CSV ingestion, SLA calculations, prediction, and alert workflows are later phases.
