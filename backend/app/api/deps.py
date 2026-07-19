"""Reusable FastAPI dependencies for protected endpoints.

No route currently uses these -- they exist so that a future protected
endpoint can add `Depends(get_current_active_user)` without re-deriving how
to pull an authenticated user out of a bearer token.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenPayload

# tokenUrl is only used to populate the OpenAPI/Swagger "Authorize" flow; no
# route is registered at this path yet.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the `User` identified by a bearer token's `sub` claim.

    Raises HTTP 401 if the token is missing, malformed, expired, or refers
    to a user that no longer exists.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = decode_access_token(token)
        token_data = TokenPayload(**claims)
        user_id = int(token_data.sub)
    except (jwt.PyJWTError, ValidationError, ValueError):
        raise credentials_error

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require that the authenticated user's account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user
