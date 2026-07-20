"""Pydantic schemas for authentication.

`Token`/`TokenPayload` describe the shape of a JWT access token and its
decoded claims; they are consumed by `app.core.security` (encode/decode),
`app.services.auth_service`, and `app.api.deps` -- no route currently
returns `Token` directly, since no login endpoint exists yet, but it is the
schema such an endpoint would use.

`RegisterRequest` is the request body for `POST /api/v1/auth/register`
(see `app.api.auth`).
"""

import re

from pydantic import BaseModel, EmailStr, field_validator

# At least one letter and one digit. Deliberately not more prescriptive
# (no forced special characters/casing) -- length plus a mix of character
# classes is a reasonable baseline without being user-hostile.
_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 128
_HAS_LETTER = re.compile(r"[A-Za-z]")
_HAS_DIGIT = re.compile(r"\d")


class RegisterRequest(BaseModel):
    """Request body for registering a new account."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Trim and lowercase the email so `a@b.com` and `A@B.com` collide.

        Uniqueness is enforced against this normalized form, both here and
        in `app.services.user_service.register_user`.
        """
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < _PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long")
        if len(value) > _PASSWORD_MAX_LENGTH:
            raise ValueError(f"Password must be at most {_PASSWORD_MAX_LENGTH} characters long")
        if not _HAS_LETTER.search(value):
            raise ValueError("Password must contain at least one letter")
        if not _HAS_DIGIT.search(value):
            raise ValueError("Password must contain at least one digit")
        return value

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_and_require_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field cannot be blank")
        return stripped


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
