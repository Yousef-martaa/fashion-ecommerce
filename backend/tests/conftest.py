"""Shared pytest fixtures for the authentication foundation tests.

`db_session` uses an isolated in-memory SQLite database containing only the
`users` table. That's sufficient here because `User` (app/models/user.py)
uses no PostgreSQL-specific column types; full-schema fidelity against the
PostgreSQL dialect is already covered separately by tests/test_migrations.py.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User

TEST_USER_PASSWORD = "correct horse battery staple"


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine, tables=[User.__table__])
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def test_user(db_session: Session) -> User:
    # Explicit id: SQLite only auto-increments a PK column that compiles to
    # exactly "INTEGER"; our model's BigInteger PK (BIGSERIAL on Postgres,
    # correctly) compiles to "BIGINT" in SQLite and does not get that
    # treatment, so this in-memory test double needs the id set explicitly.
    user = User(
        id=1,
        email="jane@example.com",
        password_hash=hash_password(TEST_USER_PASSWORD),
        first_name="Jane",
        last_name="Doe",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
