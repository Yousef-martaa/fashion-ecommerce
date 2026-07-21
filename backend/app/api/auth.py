"""Authentication routes.

Registration and login -- see docs/database-schema.md 5.1 (`users`) for the
underlying table. `app.services.user_service` and `app.services.auth_service`
hold the persistence/credential logic these routes delegate to. Logout, email
verification, token refresh, and password reset are out of scope here.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserResponse
from app.services.auth_service import InvalidCredentialsError, login_user
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


@router.post("/login", response_model=Token)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate an email/password pair and issue a JWT access token.

    Returns 401 with a generic "Invalid email or password" message whether
    the email doesn't exist or the password is wrong -- the two cases are
    deliberately indistinguishable so the response never reveals whether a
    given email is registered.
    """
    try:
        return login_user(db, data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc
