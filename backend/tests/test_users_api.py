"""Tests for GET /api/v1/users/me (app.api.users)."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User

ME_URL = f"{settings.API_V1_PREFIX}/users/me"


def _auth_headers(user_id: int | str) -> dict:
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


def test_me_succeeds_with_a_valid_token(client: TestClient, test_user: User):
    response = client.get(ME_URL, headers=_auth_headers(test_user.id))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == test_user.id
    assert body["email"] == test_user.email
    assert body["first_name"] == test_user.first_name
    assert body["last_name"] == test_user.last_name
    assert body["is_active"] is True


def test_me_never_returns_password_hash(client: TestClient, test_user: User):
    response = client.get(ME_URL, headers=_auth_headers(test_user.id))

    assert "password_hash" not in response.json()
    assert "password" not in response.json()


def test_me_rejects_a_missing_token(client: TestClient):
    response = client.get(ME_URL)

    assert response.status_code == 401


def test_me_rejects_a_garbage_token(client: TestClient):
    response = client.get(ME_URL, headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401


def test_me_rejects_an_expired_token(client: TestClient, test_user: User):
    token = create_access_token(subject=test_user.id, expires_delta=timedelta(seconds=-1))

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_rejects_a_token_for_a_deleted_or_nonexistent_user(client: TestClient):
    response = client.get(ME_URL, headers=_auth_headers(999_999))

    assert response.status_code == 401


def test_me_rejects_an_inactive_user(client: TestClient, db_session: Session, test_user: User):
    test_user.is_active = False
    db_session.commit()

    response = client.get(ME_URL, headers=_auth_headers(test_user.id))

    assert response.status_code == 403
