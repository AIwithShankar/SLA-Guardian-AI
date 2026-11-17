"""Nonpersistent, authenticated-boundary prediction service for Phase 5B."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from app.services.predictor import MODEL_VERSION, PredictionUnavailable, Predictor
from app.services.sla import SLAAssessment, TicketRecord, assess_sla, model_priority
from ml.feature_contract import validate_features


class PredictionAuthorizationError(PermissionError):
    """Raised when a caller cannot refresh a ticket prediction."""


class TicketNotFoundError(LookupError):
    """Raised when a tenant-scoped ticket cannot be found."""


@dataclass(frozen=True)
class UserContext:
    user_id: str
    organization_id: str
    role: str


class TicketRepository(Protocol):
    def get_ticket(self, ticket_id: str) -> TicketRecord | None:
        ...


@dataclass(frozen=True)
class PredictionResponse:
    ticket_id: str
    model_version: str
    prediction_timestamp: datetime
    sla_deadline: datetime | None
    breach_probability: float | None
    risk_band: str | None
    prediction_status: str
    research_only: bool
    sla_breached: bool

    def __post_init__(self) -> None:
        if self.model_version != MODEL_VERSION:
            raise ValueError("unexpected model version")
        if not self.research_only:
            raise ValueError("research-only status must remain true")
        if self.breach_probability is not None and not (
            0 <= self.breach_probability <= 1
        ):
            raise ValueError("breach probability must be between 0 and 1")


def risk_band(probability: float) -> str:
    if probability < 0.30:
        return "low"
    if probability < 0.70:
        return "medium"
    return "high"


def build_features(
    ticket: TicketRecord,
    assessment: SLAAssessment,
    at: datetime,
) -> dict[str, object]:
    if not assessment.eligible_for_prediction or assessment.remaining_hours is None:
        raise ValueError("ticket is not eligible for prediction")
    current = at.astimezone(timezone.utc)
    created = ticket.created_at.astimezone(timezone.utc)
    features = {
        "priority": model_priority(ticket.priority),
        "category": ticket.category,
        "ticket_age_hours": (current - created).total_seconds() / 3600,
        "remaining_sla_hours": assessment.remaining_hours,
        "created_hour": created.hour,
        "created_weekday": created.weekday(),
    }
    return validate_features(features)


class PredictionService:
    def __init__(self, repository: TicketRepository, predictor: Predictor) -> None:
        self._repository = repository
        self._predictor = predictor

    def predict(
        self,
        ticket_id: str,
        user: UserContext,
        at: datetime,
    ) -> PredictionResponse:
        if user.role.lower() not in {"manager", "admin"}:
            raise PredictionAuthorizationError(
                "only managers and admins may refresh predictions"
            )
        ticket = self._repository.get_ticket(ticket_id)
        if ticket is None:
            raise TicketNotFoundError("ticket not found")
        if ticket.organization_id != user.organization_id:
            raise PredictionAuthorizationError("ticket belongs to another organization")

        timestamp = at.astimezone(timezone.utc)
        assessment = assess_sla(ticket, timestamp)
        base = {
            "ticket_id": ticket.ticket_id,
            "model_version": MODEL_VERSION,
            "prediction_timestamp": timestamp,
            "sla_deadline": assessment.deadline,
            "research_only": True,
            "sla_breached": assessment.breached,
        }
        if not assessment.eligible_for_prediction:
            return PredictionResponse(
                **base,
                breach_probability=None,
                risk_band=None,
                prediction_status=f"ineligible:{assessment.reason}",
            )
        try:
            probability = self._predictor.predict_probability(
                build_features(ticket, assessment, timestamp)
            )
        except (PredictionUnavailable, ValueError):
            return PredictionResponse(
                **base,
                breach_probability=None,
                risk_band=None,
                prediction_status="unavailable",
            )
        return PredictionResponse(
            **base,
            breach_probability=probability,
            risk_band=risk_band(probability),
            prediction_status="available",
        )
