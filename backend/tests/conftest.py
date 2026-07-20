"""Shared pytest fixtures for the authentication foundation tests.

`db_session` uses an isolated in-memory SQLite database containing only the
`users` table. That's sufficient here because `User` (app/models/user.py)
uses no PostgreSQL-specific column types; full-schema fidelity against the
PostgreSQL dialect is already covered separately by tests/test_migrations.py.
"""

import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models.base import Base
from app.models.user import User

TEST_USER_PASSWORD = "correct horse battery staple"


@pytest.fixture()
def db_session():
    # StaticPool + check_same_thread=False: the `client` fixture below drives
    # this same session through a FastAPI route, which Starlette runs in a
    # worker thread (since the route is a sync `def`). A plain in-memory
    # SQLite connection is otherwise per-thread and the `users` table
    # wouldn't be visible there.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[User.__table__])
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # SQLite only auto-increments a PK column that compiles to exactly
    # "INTEGER"; our BigInteger PK (BIGSERIAL on Postgres, correctly) compiles
    # to "BIGINT" here and does not get that treatment. Code under test (e.g.
    # app.services.user_service.register_user) relies on the database
    # assigning an id, same as it would against real Postgres, so mimic
    # BIGSERIAL here by assigning one ourselves before each insert. Starts
    # well above 1 to avoid colliding with fixtures (e.g. `test_user` below)
    # that set an explicit id.
    next_id = itertools.count(1000)

    @event.listens_for(session, "before_flush")
    def _assign_ids(session, flush_context, instances):
        for obj in session.new:
            if isinstance(obj, User) and obj.id is None:
                obj.id = next(next_id)

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """A `TestClient` wired to the same isolated `db_session` used by unit tests.

    Overrides `get_db` so API-level tests hit the in-memory SQLite database
    instead of the real Postgres connection `app.core.database.get_db` would
    otherwise open.
    """

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


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
