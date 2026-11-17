"""Supabase Auth verification and trusted profile resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import quote

import httpx


class SupabaseAuthError(PermissionError):
    """Raised when a bearer token cannot be authenticated or resolved."""


class SupabaseResponse(Protocol):
    status_code: int

    def json(self) -> Any:
        ...


class SupabaseHttpClient(Protocol):
    def get(self, url: str, *, headers: dict[str, str]) -> SupabaseResponse:
        ...


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    user_id: str
    organization_id: str
    role: str
    display_name: str


def _authorization_header(token: str) -> str:
    if not token or any(char.isspace() for char in token):
        raise SupabaseAuthError("missing or malformed bearer token")
    return f"Bearer {token}"


class SupabaseAuthVerifier:
    def __init__(
        self,
        supabase_url: str,
        anon_key: str,
        client: SupabaseHttpClient | None = None,
    ) -> None:
        if not supabase_url or not anon_key:
            raise ValueError("Supabase URL and anon key are required")
        self._base_url = supabase_url.rstrip("/")
        self._anon_key = anon_key
        self._client = client or httpx.Client(timeout=5.0)

    def verify(self, access_token: str) -> AuthenticatedPrincipal:
        authorization = _authorization_header(access_token)
        headers = {
            "apikey": self._anon_key,
            "Authorization": authorization,
        }
        response = self._client.get(
            f"{self._base_url}/auth/v1/user",
            headers=headers,
        )
        if response.status_code != 200:
            raise SupabaseAuthError("Supabase rejected the access token")
        try:
            user = response.json()
            user_id = user["id"]
        except (KeyError, TypeError, ValueError) as error:
            raise SupabaseAuthError("Supabase returned an invalid user response") from error
        if not isinstance(user_id, str) or not user_id:
            raise SupabaseAuthError("Supabase user response has no valid user ID")

        profile_response = self._client.get(
            f"{self._base_url}/rest/v1/profiles"
            f"?user_id=eq.{quote(user_id, safe='')}"
            "&select=user_id,organization_id,role,display_name",
            headers={
                "apikey": self._anon_key,
                "Authorization": authorization,
            },
        )
        if profile_response.status_code != 200:
            raise SupabaseAuthError("trusted profile lookup failed")
        try:
            profiles = profile_response.json()
            profile = profiles[0]
            organization_id = profile["organization_id"]
            role = profile["role"]
            display_name = profile["display_name"]
        except (IndexError, KeyError, TypeError, ValueError) as error:
            raise SupabaseAuthError("trusted profile is missing or invalid") from error
        if role not in {"agent", "manager", "admin"}:
            raise SupabaseAuthError("trusted profile has an invalid role")
        if not all(
            isinstance(value, str) and value
            for value in (organization_id, display_name)
        ):
            raise SupabaseAuthError("trusted profile has invalid tenant data")
        return AuthenticatedPrincipal(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            display_name=display_name,
        )
