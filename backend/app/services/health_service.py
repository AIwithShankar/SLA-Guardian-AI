from app.schemas.health import HealthResponse


def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="sla-guardian-api",
        mode="foundation",
    )
