from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, predictions, tickets
from app.core.config import settings

app = FastAPI(
    title="SLA Guardian AI API",
    description="API scaffold for SLA breach prediction.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
