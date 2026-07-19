"""Shared declarative base re-export and mixins used by every model.

See docs/database-schema.md for the source design this package implements.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

__all__ = ["Base", "CreatedAtMixin", "TimestampMixin", "EMIRATES", "emirate_check"]

# Fixed set of UAE emirates the store ships to (database-schema.md, decision 7).
EMIRATES: tuple[str, ...] = (
    "Abu Dhabi",
    "Dubai",
    "Sharjah",
    "Ajman",
    "Umm Al Quwain",
    "Ras Al Khaimah",
    "Fujairah",
)


def emirate_check(column_name: str = "emirate") -> str:
    """CHECK constraint SQL restricting a column to the seven UAE emirates."""
    values = ", ".join(f"'{emirate}'" for emirate in EMIRATES)
    return f"{column_name} IN ({values})"


class CreatedAtMixin:
    """`created_at` only — for entities the schema doc gives no `updated_at`."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TimestampMixin(CreatedAtMixin):
    """`created_at` + `updated_at`, per entities that have both in the schema doc."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
