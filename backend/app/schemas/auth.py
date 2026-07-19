"""Pydantic schemas for the authentication foundation.

These describe the shape of a JWT access token and its decoded claims. They
are consumed by `app.core.security` (encode/decode), `app.services.auth_service`,
and `app.api.deps` -- no route currently returns `Token` directly, since no
login endpoint exists yet, but it is the schema such an endpoint would use.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Shape of an issued access token, as would be returned by a future login endpoint."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Validated claims decoded from a JWT access token.

    `sub` holds the authenticated user's id, encoded as a string per JWT
    convention (see `app.core.security.create_access_token`).
    """

    sub: str
    exp: int
    iat: int
