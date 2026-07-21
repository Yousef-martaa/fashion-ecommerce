"""Tests for POST /api/v1/auth/register and POST /api/v1/auth/login (app.api.auth)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token, verify_password
from app.models.user import User
from tests.conftest import TEST_USER_PASSWORD

REGISTER_URL = f"{settings.API_V1_PREFIX}/auth/register"
LOGIN_URL = f"{settings.API_V1_PREFIX}/auth/login"


def _payload(**overrides) -> dict:
    payload = {
        "email": "new.user@example.com",
        "password": "correcthorse1",
        "first_name": "New",
        "last_name": "User",
    }
    payload.update(overrides)
    return payload


def test_register_succeeds_and_returns_201(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@example.com"
    assert body["first_name"] == "New"
    assert body["last_name"] == "User"
    assert body["is_active"] is True
    assert body["is_verified"] is False
    assert "id" in body
    assert "created_at" in body


def test_register_persists_the_user(client: TestClient, db_session: Session):
    client.post(REGISTER_URL, json=_payload())

    stored = db_session.query(User).filter_by(email="new.user@example.com").one()
    assert stored.first_name == "New"


def test_register_stores_the_password_as_an_argon2_hash(client: TestClient, db_session: Session):
    client.post(REGISTER_URL, json=_payload(password="correcthorse1"))

    stored = db_session.query(User).filter_by(email="new.user@example.com").one()
    assert stored.password_hash != "correcthorse1"
    assert stored.password_hash.startswith("$argon2")
    assert verify_password("correcthorse1", stored.password_hash) is True


def test_register_never_returns_password_hash(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload())

    assert "password_hash" not in response.json()
    assert "password" not in response.json()


def test_register_rejects_a_duplicate_email(client: TestClient):
    client.post(REGISTER_URL, json=_payload())
    response = client.post(REGISTER_URL, json=_payload())

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_rejects_a_duplicate_email_case_and_whitespace_insensitively(
    client: TestClient,
):
    client.post(REGISTER_URL, json=_payload(email="Case.Test@Example.com"))
    response = client.post(REGISTER_URL, json=_payload(email="  case.test@example.com  "))

    assert response.status_code == 409


def test_register_normalizes_email_to_lowercase(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload(email="Mixed.Case@Example.COM"))

    assert response.status_code == 201
    assert response.json()["email"] == "mixed.case@example.com"


def test_register_rejects_an_invalid_email(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload(email="not-an-email"))

    assert response.status_code == 422


def test_register_rejects_a_password_that_is_too_short(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload(password="short1"))

    assert response.status_code == 422


def test_register_rejects_a_password_with_no_digit(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload(password="alllettersnodigits"))

    assert response.status_code == 422


def test_register_rejects_a_password_with_no_letter(client: TestClient):
    response = client.post(REGISTER_URL, json=_payload(password="12345678"))

    assert response.status_code == 422


def test_register_rejects_missing_required_fields(client: TestClient):
    response = client.post(REGISTER_URL, json={"email": "missing.fields@example.com"})

    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client: TestClient, test_user: User):
    response = client.post(
        LOGIN_URL, json={"email": test_user.email, "password": TEST_USER_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    claims = decode_access_token(body["access_token"])
    assert claims["sub"] == str(test_user.id)


def test_login_normalizes_email_before_matching(client: TestClient, test_user: User):
    response = client.post(
        LOGIN_URL,
        json={"email": f"  {test_user.email.upper()}  ", "password": TEST_USER_PASSWORD},
    )

    assert response.status_code == 200


def test_login_rejects_an_unknown_email(client: TestClient):
    response = client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "whatever123"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_a_wrong_password(client: TestClient, test_user: User):
    response = client.post(
        LOGIN_URL, json={"email": test_user.email, "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_unknown_email_and_wrong_password_return_the_identical_response(
    client: TestClient, test_user: User
):
    # The whole point of the generic message: an unknown email and a known
    # email with the wrong password must be indistinguishable to the caller.
    unknown_response = client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "whatever123"}
    )
    wrong_password_response = client.post(
        LOGIN_URL, json={"email": test_user.email, "password": "wrong-password"}
    )

    assert unknown_response.status_code == wrong_password_response.status_code == 401
    assert unknown_response.json() == wrong_password_response.json()


def test_login_rejects_an_invalid_email_format(client: TestClient):
    response = client.post(LOGIN_URL, json={"email": "not-an-email", "password": "whatever123"})

    assert response.status_code == 422


def test_login_rejects_missing_fields(client: TestClient):
    response = client.post(LOGIN_URL, json={"email": "someone@example.com"})

    assert response.status_code == 422


def test_login_never_returns_password_hash(client: TestClient, test_user: User):
    response = client.post(
        LOGIN_URL, json={"email": test_user.email, "password": TEST_USER_PASSWORD}
    )

    assert "password_hash" not in response.json()
