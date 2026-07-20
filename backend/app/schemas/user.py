"""Pydantic schemas for exposing `User` data over the API.

`UserResponse` is the one and only "safe" projection of a `User` row --
it deliberately omits `password_hash` (and anything else internal) so any
route that returns user data, present or future, can depend on this schema
instead of re-deriving which fields are safe to expose.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """Public-facing representation of a `User`. Never includes `password_hash`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None
    preferred_language: str
    is_active: bool
    is_verified: bool
    created_at: datetime
