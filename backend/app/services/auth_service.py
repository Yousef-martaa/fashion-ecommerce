"""Authentication service layer.

Wraps the raw building blocks in `app.core.security` with the database lookups
needed to actually authenticate a user and issue a token for them. Consumed by
`app.api.auth.login`.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, Token


class InvalidCredentialsError(Exception):
    """Raised by `login_user` when an email/password pair doesn't authenticate.

    Deliberately carries no detail about *why* (unknown email vs. wrong
    password) -- `app.api.auth.login` must respond identically either way,
    so the API never reveals whether a given email is registered.
    """


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Validate an email/password pair, returning the matching `User` or `None`.

    This checks credentials only -- it does not consider `User.is_active`.
    `login_user` (below) issues a token to any user who authenticates here
    regardless of `is_active`; enforcement for an inactive account is instead
    applied per-request to already-authenticated calls, by
    `app.api.deps.get_current_active_user`.
    """
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token_for_user(user: User) -> str:
    """Issue a JWT access token whose subject is the given user's id."""
    return create_access_token(subject=user.id)


def login_user(db: Session, data: LoginRequest) -> Token:
    """Authenticate a login request and issue an access token for it.

    Raises `InvalidCredentialsError` if `data.email` (already normalized by
    `LoginRequest.normalize_email`) doesn't match a user, or the password is
    wrong for the user it does match -- both cases are indistinguishable to
    the caller by design.
    """
    user = authenticate_user(db, data.email, data.password)
    if user is None:
        raise InvalidCredentialsError()
    return Token(access_token=create_access_token_for_user(user), token_type="bearer")
