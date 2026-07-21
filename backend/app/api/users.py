"""User account routes.

Currently only exposes the authenticated caller's own profile. Profile
updates, avatar uploads, and role management are out of scope here.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import get_current_user_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Return the authenticated caller's own profile.

    Returns 401 if the bearer token is missing, malformed, expired, or
    refers to a user that no longer exists; 403 if the account is inactive.
    """
    return get_current_user_profile(current_user)
