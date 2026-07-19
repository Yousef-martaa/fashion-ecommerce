"""Password hashing and JWT access-token primitives.

Password hashing uses Argon2 exclusively (via `argon2-cffi`) -- there is no
bcrypt fallback or dual-scheme compatibility path. All JWT parameters
(secret, algorithm, expiration) are read from `app.core.config.settings`;
nothing in this module hardcodes a secret or an expiration value.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import settings

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2, returning the encoded hash string."""
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored Argon2 hash.

    Returns `False` for a mismatch or a malformed/foreign hash rather than
    raising, so callers can treat this as a plain boolean check.
    """
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token whose `sub` claim is `subject`.

    `expires_delta` defaults to `settings.ACCESS_TOKEN_EXPIRE_MINUTES`; the
    signing secret and algorithm always come from `settings`.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload = {"sub": str(subject), "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token, returning its claims.

    Raises `jwt.PyJWTError` (e.g. `jwt.ExpiredSignatureError`,
    `jwt.InvalidTokenError`) if the token is malformed, incorrectly signed,
    or expired. Translating that into an HTTP response is left to the
    dependency layer (see `app.api.deps`), not this module.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
