from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.routes.predictions import get_prediction_service, get_principal
from app.auth.supabase import AuthenticatedPrincipal
from app.main import app
from app.services.prediction import PredictionService
from app.services.sla import TicketRecord

UTC = timezone.utc
NOW = datetime.now(UTC)


class Predictor:
    def __init__(self, probability=0.72):
        self.probability = probability

    def predict_probability(self, features):
        assert set(features) == {
            "priority",
            "category",
            "ticket_age_hours",
            "remaining_sla_hours",
            "created_hour",
            "created_weekday",
        }
        return self.probability


class Repository:
    def __init__(self, record):
        self.record = record

    def get_ticket(self, ticket_id):
        if self.record is not None and self.record.ticket_id == ticket_id:
            return self.record
        return None


def ticket(**changes):
    values = {
        "ticket_id": "ticket-1",
        "organization_id": "org-a",
        "priority": "medium",
        "category": "Category 40",
        "created_at": NOW - timedelta(hours=1),
        "status": "open",
        "sla_policy_id": "policy-1",
        "sla_deadline": NOW + timedelta(hours=23),
    }
    values.update(changes)
    return TicketRecord(**values)


def principal(role="manager", organization_id="org-a"):
    return AuthenticatedPrincipal(
        user_id="user-1",
        organization_id=organization_id,
        role=role,
        display_name=role.title(),
    )


def configure(record, role="manager", organization_id="org-a"):
    app.dependency_overrides[get_principal] = lambda: principal(
        role, organization_id
    )
    app.dependency_overrides[get_prediction_service] = lambda: PredictionService(
        Repository(record), Predictor(), require_assigned_sla=True
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_unauthenticated_request_is_denied():
    response = TestClient(app).post("/api/v1/tickets/ticket-1/predict")

    assert response.status_code == 401


@pytest.mark.parametrize("role", ["manager", "admin"])
def test_manager_and_admin_can_predict(role):
    configure(ticket(), role)

    response = TestClient(app).post(
        "/api/v1/tickets/ticket-1/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["risk_band"] == "high"
    assert response.json()["model_version"] == "phase4_research_v1"
    assert response.json()["research_only"] is True


def test_agent_is_forbidden():
    configure(ticket(), "agent")

    response = TestClient(app).post(
        "/api/v1/tickets/ticket-1/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403


def test_cross_tenant_ticket_is_forbidden():
    configure(ticket(), "admin", organization_id="org-b")

    response = TestClient(app).post(
        "/api/v1/tickets/ticket-1/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "resolved", "resolved_at": NOW},
        {
            "created_at": NOW - timedelta(hours=25),
            "sla_deadline": NOW - timedelta(hours=1),
        },
    ],
)
def test_ineligible_ticket_is_rejected(changes):
    configure(ticket(**changes))

    response = TestClient(app).post(
        "/api/v1/tickets/ticket-1/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 409


def test_missing_ticket_is_not_found():
    configure(None)

    response = TestClient(app).post(
        "/api/v1/tickets/missing/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


def test_missing_assigned_sla_policy_is_rejected():
    configure(ticket(sla_policy_id=None, sla_deadline=None))

    response = TestClient(app).post(
        "/api/v1/tickets/ticket-1/predict",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 409
