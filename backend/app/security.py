import hmac
from fastapi import Header, HTTPException, status
from backend.app.config import settings
def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """Authentication boundary for external ANPR producers."""
    if settings.REQUIRE_API_KEY and (not x_api_key or not hmac.compare_digest(x_api_key, settings.ANPR_API_KEY)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing ANPR API key")
