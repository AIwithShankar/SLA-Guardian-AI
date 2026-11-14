from app.core.config import settings


def is_supabase_configured() -> bool:
    """Return whether optional Supabase credentials are available."""
    return bool(settings.supabase_url and settings.supabase_key)
