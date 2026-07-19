"""Tests that the hand-written initial Alembic migration matches the current
model metadata, and that it renders valid SQL for the postgresql dialect.

These run entirely offline (Alembic's `--sql` / offline mode): no database
connection is opened, matching how `alembic upgrade head --sql` was used to
validate the migration during development.
"""

import io
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.models import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return cfg


@pytest.fixture(scope="module")
def alembic_cfg() -> Config:
    return _alembic_config()


def test_migration_history_has_a_single_head(alembic_cfg: Config):
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    assert len(heads) == 1


def test_upgrade_renders_without_error_for_postgresql(alembic_cfg: Config):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.upgrade(alembic_cfg, "head", sql=True)
    sql = buffer.getvalue()
    assert "CREATE TABLE" in sql


def test_upgrade_creates_exactly_the_tables_in_current_models(alembic_cfg: Config):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.upgrade(alembic_cfg, "head", sql=True)
    sql = buffer.getvalue()

    created_tables = set(re.findall(r"CREATE TABLE (\w+) \(", sql))
    # alembic_version is Alembic's own bookkeeping table, not one of ours.
    created_tables.discard("alembic_version")
    assert created_tables == set(Base.metadata.tables), (
        "migration create_table calls have drifted from Base.metadata -- "
        f"only in migration: {created_tables - set(Base.metadata.tables)}, "
        f"only in models: {set(Base.metadata.tables) - created_tables}"
    )


def test_downgrade_renders_without_error_and_drops_every_model_table(
    alembic_cfg: Config,
):
    script = ScriptDirectory.from_config(alembic_cfg)
    head = script.get_heads()[0]

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.downgrade(alembic_cfg, f"{head}:base", sql=True)
    sql = buffer.getvalue()

    dropped_tables = set(re.findall(r"DROP TABLE (\w+);", sql))
    assert set(Base.metadata.tables) <= dropped_tables


def test_migration_does_not_hardcode_usd_or_country_or_removed_fields(
    alembic_cfg: Config,
):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.upgrade(alembic_cfg, "head", sql=True)
    sql = buffer.getvalue()

    assert "'USD'" not in sql
    assert "product_images" not in sql
    assert re.search(r"\bbrand\b", sql) is None
