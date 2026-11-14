from app.db.supabase import is_supabase_configured
from app.schemas.health import HealthResponse


def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="sla-guardian-api",
        mode="supabase" if is_supabase_configured() else "mock",
    )
