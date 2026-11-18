"""Tenant-scoped ticket reads through Supabase PostgREST."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from urllib.parse import quote

import httpx

from app.services.sla import TicketRecord


class TicketRepositoryError(RuntimeError):
    """Raised when Supabase cannot provide a trusted ticket record."""


class PostgRESTResponse(Protocol):
    status_code: int

    def json(self) -> Any:
        ...


class PostgRESTClient(Protocol):
    def get(self, url: str, *, headers: dict[str, str]) -> PostgRESTResponse:
        ...


class SupabaseTicketRepository:
    """Bind every ticket query to the authenticated principal's organization."""

    def __init__(
        self,
        supabase_url: str,
        anon_key: str,
        access_token: str,
        organization_id: str,
        client: PostgRESTClient | None = None,
    ) -> None:
        if not all((supabase_url, anon_key, access_token, organization_id)):
            raise ValueError("Supabase tenant repository configuration is incomplete")
        self._base_url = supabase_url.rstrip("/")
        self._anon_key = anon_key
        self._access_token = access_token
        self._organization_id = organization_id
        self._client = client or httpx.Client(timeout=5.0)

    def get_ticket(self, ticket_id: str) -> TicketRecord | None:
        encoded_ticket_id = quote(ticket_id, safe="")
        encoded_org_id = quote(self._organization_id, safe="")
        response = self._client.get(
            f"{self._base_url}/rest/v1/tickets"
            f"?id=eq.{encoded_ticket_id}"
            f"&organization_id=eq.{encoded_org_id}"
            "&select=id,organization_id,priority,category,status,created_at,"
            "resolved_at,sla_policy_id,sla_deadline",
            headers={
                "apikey": self._anon_key,
                "Authorization": f"Bearer {self._access_token}",
            },
        )
        if response.status_code != 200:
            raise TicketRepositoryError("tenant-scoped ticket lookup failed")
        try:
            records = response.json()
            if not records:
                return None
            record = records[0]
            return TicketRecord(
                ticket_id=record["id"],
                organization_id=record["organization_id"],
                priority=record["priority"],
                category=record["category"],
                created_at=_parse_timestamp(record["created_at"]),
                status=record["status"],
                resolved_at=_parse_optional_timestamp(record.get("resolved_at")),
                sla_policy_id=record.get("sla_policy_id"),
                sla_deadline=_parse_optional_timestamp(record.get("sla_deadline")),
            )
        except (IndexError, KeyError, TypeError, ValueError) as error:
            raise TicketRepositoryError("Supabase returned an invalid ticket") from error


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("ticket timestamp is not a string")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_optional_timestamp(value: Any) -> datetime | None:
    return None if value is None else _parse_timestamp(value)
