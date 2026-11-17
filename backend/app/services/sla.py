"""Deterministic, UTC-aware provisional SLA calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final

SLA_POLICY_HOURS: Final = {
    "1 - Critical": 4,
    "2 - High": 8,
    "3 - Moderate": 24,
    "4 - Low": 72,
}

_PRIORITY_ALIASES: Final = {
    "critical": "1 - Critical",
    "high": "2 - High",
    "medium": "3 - Moderate",
    "moderate": "3 - Moderate",
    "low": "4 - Low",
}


@dataclass(frozen=True)
class TicketRecord:
    ticket_id: str
    organization_id: str
    priority: str
    category: str
    created_at: datetime
    status: str
    resolved_at: datetime | None = None
    sla_deadline: datetime | None = None


@dataclass(frozen=True)
class SLAAssessment:
    deadline: datetime | None
    remaining_hours: float | None
    breached: bool
    eligible_for_prediction: bool
    reason: str | None = None


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def model_priority(priority: str) -> str:
    """Return the notebook's source priority representation."""

    if priority in SLA_POLICY_HOURS:
        return priority
    try:
        return _PRIORITY_ALIASES[priority.strip().lower()]
    except KeyError as error:
        raise ValueError(f"unsupported SLA priority: {priority}") from error


def assess_sla(ticket: TicketRecord, at: datetime) -> SLAAssessment:
    """Calculate deadline, breach state, and future-prediction eligibility."""

    current = _utc(at)
    created = _utc(ticket.created_at)
    resolved = _utc(ticket.resolved_at) if ticket.resolved_at else None

    if ticket.sla_deadline is not None:
        deadline = _utc(ticket.sla_deadline)
    else:
        try:
            target_hours = SLA_POLICY_HOURS[model_priority(ticket.priority)]
        except ValueError as error:
            return SLAAssessment(None, None, False, False, str(error))
        deadline = created + timedelta(hours=target_hours)

    if deadline < created:
        return SLAAssessment(
            deadline, None, False, False, "SLA deadline precedes ticket creation"
        )

    if resolved is not None:
        breached = resolved > deadline
        return SLAAssessment(
            deadline,
            (deadline - current).total_seconds() / 3600,
            breached,
            False,
            "ticket is resolved",
        )

    breached = current >= deadline
    remaining_hours = (deadline - current).total_seconds() / 3600
    if breached:
        return SLAAssessment(
            deadline, remaining_hours, True, False, "ticket is already overdue"
        )
    if ticket.status not in {"open", "in_progress"}:
        return SLAAssessment(
            deadline, remaining_hours, False, False, "ticket status is not predictive"
        )
    return SLAAssessment(deadline, remaining_hours, False, True)
