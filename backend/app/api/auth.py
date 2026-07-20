"""Authentication routes.

Currently registration only -- see docs/database-schema.md 5.1 (`users`) for
the underlying table, and `app.services.user_service` for the persistence
logic this route delegates to. Login, logout, email verification, and token
refresh are out of scope here; `app.core.security`/`app.api.deps` already
have the JWT building blocks a future login endpoint would use.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse
from app.services.user_service import EmailAlreadyRegisteredError, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Create a new user account.

    Returns 201 with the created user (never `password_hash`) on success,
    or 409 if the email is already registered. Malformed input (invalid
    email, weak password, blank name) is rejected with 422 by
    `RegisterRequest`'s own validation before this handler runs.
    """
    try:
        user = register_user(db, data)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc
    return UserResponse.model_validate(user)
