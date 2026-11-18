import pytest

from app.auth.supabase import SupabaseAuthError, SupabaseAuthVerifier
from app.repositories.supabase_tickets import (
    SupabaseTicketRepository,
    TicketRepositoryError,
)


class Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class Client:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def get(self, url, *, headers):
        self.requests.append((url, headers))
        return self.responses.pop(0)


def test_auth_verifier_uses_supabase_user_and_trusted_profile():
    client = Client(
        [
            Response(200, {"id": "user-1"}),
            Response(
                200,
                [
                    {
                        "user_id": "user-1",
                        "organization_id": "org-1",
                        "role": "manager",
                        "display_name": "Manager",
                    }
                ],
            ),
        ]
    )

    principal = SupabaseAuthVerifier(
        "https://example.supabase.co", "anon-key", client
    ).verify("token-value")

    assert principal.organization_id == "org-1"
    assert principal.role == "manager"
    assert client.requests[0][1]["Authorization"] == "Bearer token-value"
    assert "&organization_id=eq." not in client.requests[1][0]


def test_auth_verifier_rejects_invalid_token_and_profile():
    with pytest.raises(SupabaseAuthError):
        SupabaseAuthVerifier(
            "https://example.supabase.co",
            "anon-key",
            Client([Response(401, {"message": "invalid"})]),
        ).verify("token-value")

    with pytest.raises(SupabaseAuthError):
        SupabaseAuthVerifier(
            "https://example.supabase.co",
            "anon-key",
            Client([Response(200, {"id": "user-1"}), Response(200, [])]),
        ).verify("token-value")


def test_ticket_repository_binds_query_to_authenticated_organization():
    client = Client(
        [
            Response(
                200,
                [
                    {
                        "id": "ticket-1",
                        "organization_id": "org-1",
                        "priority": "medium",
                        "category": "Category 40",
                        "status": "open",
                        "created_at": "2026-11-17T10:00:00Z",
                        "resolved_at": None,
                        "sla_policy_id": "policy-1",
                        "sla_deadline": "2026-11-18T10:00:00Z",
                    }
                ],
            )
        ]
    )
    repository = SupabaseTicketRepository(
        "https://example.supabase.co",
        "anon-key",
        "user-token",
        "org-1",
        client,
    )

    record = repository.get_ticket("ticket-1")

    assert record is not None
    assert record.organization_id == "org-1"
    assert "organization_id=eq.org-1" in client.requests[0][0]
    assert client.requests[0][1]["Authorization"] == "Bearer user-token"


def test_ticket_repository_surfaces_database_errors():
    repository = SupabaseTicketRepository(
        "https://example.supabase.co",
        "anon-key",
        "user-token",
        "org-1",
        Client([Response(500, {"message": "failure"})]),
    )

    with pytest.raises(TicketRepositoryError):
        repository.get_ticket("ticket-1")
