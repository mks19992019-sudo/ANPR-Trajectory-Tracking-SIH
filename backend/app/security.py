from fastapi import Header, HTTPException, Query, Security, status
from typing import Optional
from backend.app.config import settings

def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Query(None)
) -> bool:
    """
    Validates API key for secure police ANPR ingestion and administrative endpoints.
    In development mode (REQUIRE_API_KEY=False), missing keys are permitted.
    """
    if not settings.REQUIRE_API_KEY:
        return True

    key = x_api_key or api_key
    if not key or key != settings.ANPR_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing ANPR API authentication key.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return True
