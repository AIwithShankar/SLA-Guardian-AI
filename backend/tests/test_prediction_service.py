from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.predictor import PredictionUnavailable
from app.services.prediction import (
    PredictionAuthorizationError,
    PredictionService,
    UserContext,
    build_features,
    risk_band,
)
from app.services.sla import TicketRecord, assess_sla

UTC = timezone.utc
NOW = datetime(2026, 11, 17, 12, 0, tzinfo=UTC)


def ticket(**changes):
    values = {
        "ticket_id": "T-1",
        "organization_id": "ORG-1",
        "priority": "3 - Moderate",
        "category": "Category 40",
        "created_at": NOW - timedelta(hours=1),
        "status": "open",
    }
    values.update(changes)
    return TicketRecord(**values)


class Repository:
    def __init__(self, record):
        self.record = record

    def get_ticket(self, ticket_id):
        return self.record if self.record.ticket_id == ticket_id else None


class Predictor:
    def __init__(self, probability=0.68, error=None):
        self.probability = probability
        self.error = error
        self.features = []

    def predict_probability(self, features):
        self.features.append(features)
        if self.error:
            raise self.error
        return self.probability


def service(record, predictor=None):
    return PredictionService(Repository(record), predictor or Predictor())


def test_sla_deadline_and_exact_boundary_are_deterministic():
    record = ticket(created_at=NOW)
    assessment = assess_sla(record, NOW + timedelta(hours=24))

    assert assessment.deadline == NOW + timedelta(hours=24)
    assert assessment.breached is True
    assert assessment.eligible_for_prediction is False


def test_resolved_ticket_is_ineligible():
    record = ticket(resolved_at=NOW, status="resolved")

    assessment = assess_sla(record, NOW)

    assert assessment.eligible_for_prediction is False
    assert assessment.reason == "ticket is resolved"


def test_overdue_ticket_is_ineligible():
    record = ticket(created_at=NOW - timedelta(hours=25))

    assessment = assess_sla(record, NOW)

    assert assessment.breached is True
    assert assessment.eligible_for_prediction is False


def test_valid_feature_construction_uses_exact_six_features():
    record = ticket(created_at=NOW - timedelta(hours=1))
    assessment = assess_sla(record, NOW)

    features = build_features(record, assessment, NOW)

    assert set(features) == {
        "priority",
        "category",
        "ticket_age_hours",
        "remaining_sla_hours",
        "created_hour",
        "created_weekday",
    }
    assert features["priority"] == "3 - Moderate"


def test_feature_construction_rejects_missing_or_invalid_values():
    record = ticket(created_at=NOW - timedelta(hours=1))
    assessment = assess_sla(record, NOW)

    with pytest.raises(ValueError):
        build_features(ticket(priority="unknown"), assessment, NOW)
    with pytest.raises(ValueError):
        build_features(ticket(created_at=NOW + timedelta(hours=1)), assessment, NOW)


@pytest.mark.parametrize(
    ("probability", "expected"),
    [(0.2999, "low"), (0.30, "medium"), (0.6999, "medium"), (0.70, "high")],
)
def test_risk_band_thresholds(probability, expected):
    assert risk_band(probability) == expected


def test_prediction_response_contains_version_status_and_features():
    predictor = Predictor(0.70)
    response = service(ticket(), predictor).predict(
        "T-1",
        UserContext("U-1", "ORG-1", "manager"),
        NOW,
    )

    assert response.prediction_status == "available"
    assert response.model_version == "phase4_research_v1"
    assert response.research_only is True
    assert response.risk_band == "high"
    assert set(predictor.features[0]) == {
        "priority",
        "category",
        "ticket_age_hours",
        "remaining_sla_hours",
        "created_hour",
        "created_weekday",
    }


def test_model_unavailable_returns_explicit_status():
    response = service(
        ticket(),
        Predictor(error=PredictionUnavailable("unavailable")),
    ).predict("T-1", UserContext("U-1", "ORG-1", "manager"), NOW)

    assert response.prediction_status == "unavailable"
    assert response.breach_probability is None
    assert response.sla_deadline is not None


@pytest.mark.parametrize("role", ["agent", "viewer"])
def test_unauthorized_roles_are_rejected(role):
    with pytest.raises(PredictionAuthorizationError):
        service(ticket()).predict("T-1", UserContext("U-1", "ORG-1", role), NOW)


def test_cross_tenant_access_is_rejected():
    with pytest.raises(PredictionAuthorizationError):
        service(ticket()).predict(
            "T-1", UserContext("U-1", "ORG-2", "admin"), NOW
        )


def test_repeated_deterministic_inference():
    predictor = Predictor(0.42)
    prediction_service = service(ticket(), predictor)
    user = UserContext("U-1", "ORG-1", "admin")

    first = prediction_service.predict("T-1", user, NOW)
    second = prediction_service.predict("T-1", user, NOW)

    assert first.breach_probability == second.breach_probability == 0.42


def test_prediction_route_is_not_public_without_authentication():
    response = TestClient(app).post("/api/v1/tickets/T-1/predict")

    assert response.status_code == 404
