"""Tests for app.core.security: Argon2 password hashing and JWT access tokens."""

from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_uses_argon2():
    hashed = hash_password("s3cret-pass")
    assert hashed.startswith("$argon2")


def test_hash_password_is_salted():
    # Same input, two calls -> different hashes (random salt per call).
    assert hash_password("s3cret-pass") != hash_password("s3cret-pass")


def test_hash_password_does_not_leak_the_plaintext():
    assert "s3cret-pass" not in hash_password("s3cret-pass")


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("s3cret-pass")
    assert verify_password("s3cret-pass", hashed) is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("s3cret-pass")
    assert verify_password("wrong-pass", hashed) is False


def test_verify_password_rejects_a_malformed_hash_instead_of_raising():
    assert verify_password("anything", "not-a-real-argon2-hash") is False


def test_create_access_token_uses_algorithm_and_secret_from_settings():
    token = create_access_token(subject=1)
    header = jwt.get_unverified_header(token)
    assert header["alg"] == settings.ALGORITHM
    # Round-trips using the app's own configured secret.
    decode_access_token(token)


def test_create_access_token_default_expiry_comes_from_settings():
    token = create_access_token(subject=1)
    claims = decode_access_token(token)
    assert claims["exp"] - claims["iat"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_create_access_token_accepts_an_explicit_expires_delta():
    token = create_access_token(subject=1, expires_delta=timedelta(minutes=5))
    claims = decode_access_token(token)
    assert claims["exp"] - claims["iat"] == 5 * 60


def test_create_access_token_stores_subject_as_string():
    token = create_access_token(subject=123)
    claims = decode_access_token(token)
    assert claims["sub"] == "123"


def test_decode_access_token_rejects_an_expired_token():
    token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_decode_access_token_rejects_a_tampered_token():
    token = create_access_token(subject=1)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered)


def test_decode_access_token_rejects_a_token_signed_with_a_different_secret():
    forged = jwt.encode(
        {"sub": "1"}, "a-totally-different-secret-key-value-here", algorithm=settings.ALGORITHM
    )
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(forged)
