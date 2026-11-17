"""Run non-destructive Supabase Auth and RLS checks against a test project."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any

import httpx


REQUIRED_ENVIRONMENT = (
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_ADMIN_A_EMAIL",
    "SUPABASE_ADMIN_A_PASSWORD",
    "SUPABASE_ADMIN_B_EMAIL",
    "SUPABASE_ADMIN_B_PASSWORD",
)


@dataclass(frozen=True)
class TestUser:
    token: str
    user_id: str
    organization_id: str
    role: str


class IntegrationFailure(RuntimeError):
    """Raised when a required cloud assertion fails."""


def _require_environment() -> dict[str, str]:
    missing = [
        name
        for name in REQUIRED_ENVIRONMENT
        if not os.environ.get(name)
    ]
    if missing:
        raise IntegrationFailure(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return {name: os.environ[name] for name in REQUIRED_ENVIRONMENT}


def _headers(key: str, token: str | None = None) -> dict[str, str]:
    headers = {"apikey": key}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _assert_status(
    name: str,
    response: httpx.Response,
    accepted: set[int],
) -> None:
    if response.status_code not in accepted:
        raise IntegrationFailure(
            f"{name}: unexpected HTTP status {response.status_code}"
        )
    print(f"PASS {name}: HTTP {response.status_code}")


def _login(
    client: httpx.Client,
    base_url: str,
    key: str,
    email: str,
    password: str,
    label: str,
) -> TestUser:
    response = client.post(
        f"{base_url}/auth/v1/token?grant_type=password",
        headers=_headers(key),
        json={"email": email, "password": password},
    )
    _assert_status(f"{label} password login", response, {200})
    payload = _json(response)
    if not isinstance(payload, dict) or not isinstance(
        payload.get("access_token"), str
    ):
        raise IntegrationFailure(f"{label} login returned no access token")
    token = payload["access_token"]

    user_response = client.get(
        f"{base_url}/auth/v1/user",
        headers=_headers(key, token),
    )
    _assert_status(f"{label} authenticated user", user_response, {200})
    user_payload = _json(user_response)
    user_id = user_payload.get("id") if isinstance(user_payload, dict) else None
    if not isinstance(user_id, str) or not user_id:
        raise IntegrationFailure(f"{label} user response has no ID")

    profile_response = client.get(
        f"{base_url}/rest/v1/profiles"
        f"?user_id=eq.{user_id}"
        "&select=user_id,organization_id,role",
        headers=_headers(key, token),
    )
    _assert_status(f"{label} trusted profile", profile_response, {200})
    profiles = _json(profile_response)
    if not isinstance(profiles, list) or len(profiles) != 1:
        raise IntegrationFailure(f"{label} trusted profile is not unique")
    profile = profiles[0]
    organization_id = profile.get("organization_id")
    role = profile.get("role")
    if not isinstance(organization_id, str) or role != "admin":
        raise IntegrationFailure(f"{label} profile is not an admin profile")
    return TestUser(token, user_id, organization_id, role)


def _tickets(
    client: httpx.Client,
    base_url: str,
    key: str,
    user: TestUser,
    organization_id: str,
    label: str,
) -> list[dict[str, Any]]:
    response = client.get(
        f"{base_url}/rest/v1/tickets"
        f"?organization_id=eq.{organization_id}"
        "&select=id,organization_id,category",
        headers=_headers(key, user.token),
    )
    _assert_status(label, response, {200})
    payload = _json(response)
    if not isinstance(payload, list):
        raise IntegrationFailure(f"{label}: response was not a list")
    return payload


def _assert_only_organization(
    rows: list[dict[str, Any]],
    expected_organization_id: str,
    label: str,
) -> None:
    if any(row.get("organization_id") != expected_organization_id for row in rows):
        raise IntegrationFailure(f"{label}: cross-organization row returned")
    print(f"PASS {label}: {len(rows)} rows are organization-scoped")


def _rollback_patch(
    client: httpx.Client,
    base_url: str,
    key: str,
    token: str,
    table: str,
    query: str,
    body: dict[str, str],
    label: str,
) -> httpx.Response:
    return client.patch(
        f"{base_url}/rest/v1/{table}?{query}",
        headers={
            **_headers(key, token),
            "Prefer": "tx=rollback,return=representation",
        },
        json=body,
    )


def run() -> int:
    values = _require_environment()
    base_url = values["SUPABASE_URL"].rstrip("/")
    key = values["SUPABASE_PUBLISHABLE_KEY"]

    with httpx.Client(timeout=10.0) as client:
        admin_a = _login(
            client,
            base_url,
            key,
            values["SUPABASE_ADMIN_A_EMAIL"],
            values["SUPABASE_ADMIN_A_PASSWORD"],
            "Admin A",
        )
        admin_b = _login(
            client,
            base_url,
            key,
            values["SUPABASE_ADMIN_B_EMAIL"],
            values["SUPABASE_ADMIN_B_PASSWORD"],
            "Admin B",
        )
        if admin_a.organization_id == admin_b.organization_id:
            raise IntegrationFailure("test users resolved to the same organization")

        tickets_a = _tickets(
            client, base_url, key, admin_a, admin_a.organization_id,
            "Admin A own-ticket read",
        )
        _assert_only_organization(tickets_a, admin_a.organization_id,
                                  "Admin A own-ticket read")
        tickets_b = _tickets(
            client, base_url, key, admin_b, admin_b.organization_id,
            "Admin B own-ticket read",
        )
        _assert_only_organization(tickets_b, admin_b.organization_id,
                                  "Admin B own-ticket read")

        a_cross = _tickets(
            client, base_url, key, admin_a, admin_b.organization_id,
            "Admin A cross-organization read",
        )
        if a_cross:
            raise IntegrationFailure("Admin A read Organization B tickets")
        print("PASS Admin A cross-organization read: no rows")

        b_cross = _tickets(
            client, base_url, key, admin_b, admin_a.organization_id,
            "Admin B cross-organization read",
        )
        if b_cross:
            raise IntegrationFailure("Admin B read Organization A tickets")
        print("PASS Admin B cross-organization read: no rows")

        if tickets_b:
            b_ticket = tickets_b[0]
            response = _rollback_patch(
                client,
                base_url,
                key,
                admin_a.token,
                "tickets",
                f"id=eq.{b_ticket['id']}",
                {"category": str(b_ticket["category"])},
                "Admin A cross-organization modification",
            )
            if response.status_code in {200, 204} and _json(response):
                raise IntegrationFailure(
                    "Admin A received a cross-organization ticket update"
                )
            print(
                "PASS Admin A cross-organization modification: "
                f"HTTP {response.status_code}, no returned row"
            )
        else:
            print("SKIP cross-organization modification: Organization B has no tickets")

        profile_query = f"user_id=eq.{admin_a.user_id}"
        response = _rollback_patch(
            client,
            base_url,
            key,
            admin_a.token,
            "profiles",
            profile_query,
            {"role": "manager"},
            "Admin A self-role modification",
        )
        if response.status_code in {200, 204} and _json(response):
            raise IntegrationFailure("Admin A self-role modification was accepted")
        print(
            "PASS Admin A self-role modification: "
            f"HTTP {response.status_code}, no returned row"
        )

        response = _rollback_patch(
            client,
            base_url,
            key,
            admin_a.token,
            "profiles",
            profile_query,
            {"organization_id": admin_b.organization_id},
            "Admin A self-organization modification",
        )
        if response.status_code in {200, 204} and _json(response):
            raise IntegrationFailure(
                "Admin A self-organization modification was accepted"
            )
        print(
            "PASS Admin A self-organization modification: "
            f"HTTP {response.status_code}, no returned row"
        )

        anonymous = client.get(
            f"{base_url}/rest/v1/tickets?select=id",
            headers=_headers(key),
        )
        _assert_status("Anonymous ticket read", anonymous, {401, 403})

    print("ALL CONFIGURED SUPABASE RLS CHECKS PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (httpx.HTTPError, IntegrationFailure) as error:
        print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
