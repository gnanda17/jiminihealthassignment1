"""API key authentication."""

from fastapi import Header, HTTPException, status

from app.config import get_settings
from app.models import User


async def get_current_user(
    x_api_key: str = Header(..., description="API key for authentication"),
) -> User:
    """Validate API key and return user context.

    Raises:
        HTTPException: 401 if API key is missing or invalid.
    """
    settings = get_settings()
    user = settings.api_keys.get(x_api_key)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return User(**user)
