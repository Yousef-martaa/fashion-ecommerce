"""Authentication service layer.

Wraps the raw building blocks in `app.core.security` with the database lookups
needed to actually authenticate a user and issue a token for them. No route
calls into this yet -- it exists so a future login endpoint (out of scope for
this task) has a single, tested place to call into.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Validate an email/password pair, returning the matching `User` or `None`.

    This checks credentials only -- it does not consider `User.is_active`.
    Whether an inactive account may actually log in is a decision for the
    (not-yet-implemented) login endpoint to make; enforcement for already
    -authenticated requests is handled by `app.api.deps.get_current_active_user`.
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
