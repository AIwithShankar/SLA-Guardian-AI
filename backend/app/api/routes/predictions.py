"""Authenticated ticket prediction endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict

from app.auth.supabase import (
    AuthenticatedPrincipal,
    SupabaseAuthError,
    SupabaseAuthVerifier,
)
from app.core.config import settings
from app.repositories.supabase_tickets import (
    SupabaseTicketRepository,
    TicketRepositoryError,
)
from app.services.prediction import (
    PredictionAuthorizationError,
    PredictionResponse,
    PredictionService,
    TicketNotFoundError,
    UserContext,
)
from app.services.predictor import TrustedModelPredictor

router = APIRouter(prefix="/api/v1", tags=["predictions"])
_bearer = HTTPBearer(auto_error=False)
_predictor = TrustedModelPredictor()


class PredictionResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    model_version: str
    prediction_timestamp: datetime
    sla_deadline: datetime | None
    breach_probability: float | None
    risk_band: str | None
    prediction_status: str
    research_only: bool
    sla_breached: bool


def get_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer)
    ],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def get_principal(
    access_token: Annotated[str, Depends(get_access_token)],
) -> AuthenticatedPrincipal:
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured",
        )
    try:
        return SupabaseAuthVerifier(
            settings.supabase_url,
            settings.supabase_anon_key,
        ).verify(access_token)
    except (SupabaseAuthError, OSError, httpx.HTTPError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def get_prediction_service(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_principal)],
    access_token: Annotated[str, Depends(get_access_token)],
) -> PredictionService:
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase repository is not configured",
        )
    repository = SupabaseTicketRepository(
        settings.supabase_url,
        settings.supabase_anon_key,
        access_token,
        principal.organization_id,
    )
    return PredictionService(
        repository,
        _predictor,
        require_assigned_sla=True,
    )


@router.post(
    "/tickets/{ticket_id}/predict",
    response_model=PredictionResponseModel,
)
def predict_ticket(
    ticket_id: str,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_principal)],
    prediction_service: Annotated[
        PredictionService, Depends(get_prediction_service)
    ],
) -> PredictionResponse:
    try:
        response = prediction_service.predict(
            ticket_id,
            UserContext(
                user_id=principal.user_id,
                organization_id=principal.organization_id,
                role=principal.role,
            ),
            datetime.now(timezone.utc),
        )
        if response.prediction_status.startswith("ineligible:"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=response.prediction_status.removeprefix("ineligible:"),
            )
        if response.prediction_status == "unavailable":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Research model is unavailable",
            )
        return response
    except PredictionAuthorizationError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except TicketNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        ) from error
    except TicketRepositoryError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Tenant-scoped ticket lookup failed",
        ) from error
