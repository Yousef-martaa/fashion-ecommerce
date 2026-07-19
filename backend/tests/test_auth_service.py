"""Tests for app.services.auth_service."""

from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import authenticate_user, create_access_token_for_user
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
