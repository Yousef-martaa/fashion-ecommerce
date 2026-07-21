"""Tests for app.services.auth_service."""

import pytest
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.services.auth_service import (
    InvalidCredentialsError,
    authenticate_user,
    create_access_token_for_user,
    login_user,
)
from tests.conftest import TEST_USER_PASSWORD


def test_authenticate_user_with_correct_credentials(db_session: Session, test_user: User):
    authenticated = authenticate_user(db_session, test_user.email, TEST_USER_PASSWORD)
    assert authenticated is not None
    assert authenticated.id == test_user.id


def test_authenticate_user_with_wrong_password(db_session: Session, test_user: User):
    assert authenticate_user(db_session, test_user.email, "wrong-password") is None


def test_authenticate_user_with_unknown_email(db_session: Session):
    assert authenticate_user(db_session, "nobody@example.com", "whatever") is None


def test_create_access_token_for_user_embeds_the_users_id(test_user: User):
    token = create_access_token_for_user(test_user)
    claims = decode_access_token(token)
    assert claims["sub"] == str(test_user.id)


def test_login_user_with_correct_credentials_returns_a_token(db_session: Session, test_user: User):
    token = login_user(db_session, LoginRequest(email=test_user.email, password=TEST_USER_PASSWORD))

    assert token.token_type == "bearer"
    claims = decode_access_token(token.access_token)
    assert claims["sub"] == str(test_user.id)


def test_login_user_normalizes_email_before_matching(db_session: Session, test_user: User):
    # LoginRequest normalizes casing/whitespace on construction, so a
    # differently-cased/padded email for the same account still logs in.
    request = LoginRequest(email=f"  {test_user.email.upper()}  ", password=TEST_USER_PASSWORD)
    token = login_user(db_session, request)

    claims = decode_access_token(token.access_token)
    assert claims["sub"] == str(test_user.id)


def test_login_user_with_wrong_password_raises_invalid_credentials(
    db_session: Session, test_user: User
):
    with pytest.raises(InvalidCredentialsError):
        login_user(db_session, LoginRequest(email=test_user.email, password="wrong-password"))


def test_login_user_with_unknown_email_raises_invalid_credentials(db_session: Session):
    with pytest.raises(InvalidCredentialsError):
        login_user(db_session, LoginRequest(email="nobody@example.com", password="whatever123"))
