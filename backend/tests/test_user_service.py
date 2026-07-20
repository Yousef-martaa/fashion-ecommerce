"""Tests for app.services.user_service."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.user_service import EmailAlreadyRegisteredError, register_user


class _FakeDriverError:
    """Stand-in for a DBAPI error (`IntegrityError.orig`) with just a message."""

    def __init__(self, message: str):
        self._message = message

    def __str__(self) -> str:
        return self._message


def _register_request(**overrides) -> RegisterRequest:
    data = {
        "email": "new.user@example.com",
        "password": "correcthorse1",
        "first_name": "New",
        "last_name": "User",
    }
    data.update(overrides)
    return RegisterRequest(**data)


def test_register_user_creates_and_persists_a_user(db_session: Session):
    user = register_user(db_session, _register_request())

    assert user.id is not None
    stored = db_session.get(User, user.id)
    assert stored is not None
    assert stored.email == "new.user@example.com"
    assert stored.first_name == "New"
    assert stored.last_name == "User"


def test_register_user_hashes_the_password(db_session: Session):
    user = register_user(db_session, _register_request(password="correcthorse1"))

    assert user.password_hash != "correcthorse1"
    assert user.password_hash.startswith("$argon2")
    assert verify_password("correcthorse1", user.password_hash) is True


def test_register_user_commits_exactly_once(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    real_commit = db_session.commit
    commit_calls = []

    def _counting_commit():
        commit_calls.append(1)
        return real_commit()

    monkeypatch.setattr(db_session, "commit", _counting_commit)

    register_user(db_session, _register_request())

    assert len(commit_calls) == 1


def test_register_user_rejects_a_duplicate_email(db_session: Session, test_user: User):
    with pytest.raises(EmailAlreadyRegisteredError):
        register_user(db_session, _register_request(email=test_user.email))


def test_register_user_treats_email_as_already_normalized(db_session: Session, test_user: User):
    # RegisterRequest normalizes email casing/whitespace before this layer
    # ever sees it, so a differently-cased duplicate is caught by the
    # normalization test in test_auth_api.py; this confirms the service
    # itself compares the email verbatim (case-sensitively) against what it
    # is given.
    register_user(db_session, _register_request(email="totally.different@example.com"))
    with pytest.raises(EmailAlreadyRegisteredError):
        register_user(db_session, _register_request(email="totally.different@example.com"))


def test_register_user_converts_email_unique_integrity_error(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
):
    # Simulates the race the pre-check can't close: two requests both pass
    # the SELECT before either commits, so the second's INSERT is the one
    # that actually hits the `users.email` UNIQUE constraint at commit time.
    def _raise_integrity_error():
        raise IntegrityError(
            "INSERT INTO users ...",
            {},
            _FakeDriverError("UNIQUE constraint failed: users.email"),
        )

    monkeypatch.setattr(db_session, "commit", _raise_integrity_error)

    with pytest.raises(EmailAlreadyRegisteredError):
        register_user(db_session, _register_request())


def test_register_user_reraises_unrelated_integrity_error(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
):
    # A NOT NULL/FK/other integrity failure must never be misreported as a
    # duplicate email -- it should propagate as-is.
    def _raise_integrity_error():
        raise IntegrityError(
            "INSERT INTO users ...",
            {},
            _FakeDriverError("NOT NULL constraint failed: users.first_name"),
        )

    monkeypatch.setattr(db_session, "commit", _raise_integrity_error)

    with pytest.raises(IntegrityError):
        register_user(db_session, _register_request())
