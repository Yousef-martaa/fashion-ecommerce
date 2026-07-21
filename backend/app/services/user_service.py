"""User account service layer.

Holds registration and profile retrieval. Sits between the `auth`/`users`
routes and the `User` model/`app.core.security`, the same layering
`auth_service.py` uses for authentication.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse

# Postgres's default auto-generated name for the unnamed `UniqueConstraint('email')`
# on `users` (see the initial Alembic migration and docs/database-schema.md, 5.1)
# is "<table>_<column>_key".
_USERS_EMAIL_UNIQUE_CONSTRAINT = "users_email_key"


class EmailAlreadyRegisteredError(Exception):
    """Raised by `register_user` when the (normalized) email is already taken."""


def _is_email_unique_violation(exc: IntegrityError) -> bool:
    """Whether `exc` is specifically the `users.email` UNIQUE constraint firing.

    Psycopg2 exposes the violated constraint's name via `orig.diag.constraint_name`,
    which is the reliable signal against Postgres. SQLite (used by the test suite)
    has no such structured field, so as a fallback this inspects the driver's error
    message for both "unique" and "email" -- good enough to keep NOT NULL, foreign
    key, and unrelated UNIQUE violations from being misreported as a duplicate email.
    """
    orig = exc.orig
    constraint_name = getattr(getattr(orig, "diag", None), "constraint_name", None)
    if constraint_name is not None:
        return constraint_name == _USERS_EMAIL_UNIQUE_CONSTRAINT
    message = str(orig).lower()
    return "unique" in message and "email" in message


def register_user(db: Session, data: RegisterRequest) -> User:
    """Create and persist a new `User` from a validated `RegisterRequest`.

    Raises `EmailAlreadyRegisteredError` if a user with this email (already
    normalized by `RegisterRequest.normalize_email`) already exists, whether
    caught by the pre-check below or, under a concurrent request for the same
    email, by the `users.email` UNIQUE constraint at commit time -- see
    `_is_email_unique_violation`. The password is never stored in plaintext
    -- only its Argon2 hash is.
    """
    existing = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if existing is not None:
        raise EmailAlreadyRegisteredError(data.email)

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_email_unique_violation(exc):
            raise EmailAlreadyRegisteredError(data.email) from exc
        raise
    db.refresh(user)
    return user


def get_current_user_profile(user: User) -> UserResponse:
    """Build the safe, public-facing representation of the authenticated user.

    `user` is already resolved by `app.api.deps.get_current_active_user`; this just
    keeps the `User` -> `UserResponse` projection (never `password_hash`) in
    the service layer rather than the route.
    """
    return UserResponse.model_validate(user)
