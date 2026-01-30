"""User model."""

from app.models.base import CamelModel


class User(CamelModel):
    """Authenticated user context."""

    user_id: str
    name: str
