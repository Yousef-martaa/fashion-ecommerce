"""Tests for app.api.deps: the get_current_user / get_current_active_user
dependencies that a future protected endpoint would use.
"""

from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_user
from app.core.security import create_access_token
from app.models.user import User


def test_get_current_user_with_a_valid_token(db_session: Session, test_user: User):
    token = create_access_token(subject=test_user.id)
    resolved = get_current_user(token=token, db=db_session)
    assert resolved.id == test_user.id


def test_get_current_user_with_a_garbage_token(db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="not-a-jwt", db=db_session)
    assert exc_info.value.status_code == 401


def test_get_current_user_with_an_expired_token(db_session: Session, test_user: User):
    token = create_access_token(subject=test_user.id, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == 401


def test_get_current_user_for_a_deleted_or_nonexistent_user(db_session: Session):
    token = create_access_token(subject=999_999)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == 401


def test_get_current_active_user_returns_an_active_user(test_user: User):
    assert get_current_active_user(current_user=test_user) is test_user


def test_get_current_active_user_rejects_an_inactive_user(test_user: User):
    test_user.is_active = False
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=test_user)
    assert exc_info.value.status_code == 403
