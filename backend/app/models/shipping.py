"""`shipping_methods` and `shipping_rates` (database-schema.md, 5.8-5.9).

Rates vary by emirate; methods are the reusable standard/express/free definitions
(decision 19).
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, emirate_check

if TYPE_CHECKING:
    from app.models.order import Order


class ShippingMethod(TimestampMixin, Base):
    __tablename__ = "shipping_methods"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_days_min: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_days_max: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    rates: Mapped[list["ShippingRate"]] = relationship(
        back_populates="shipping_method", cascade="all, delete-orphan", passive_deletes=True
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="shipping_method")


class ShippingRate(TimestampMixin, Base):
    __tablename__ = "shipping_rates"
    __table_args__ = (
        CheckConstraint(emirate_check(), name="ck_shipping_rates_emirate"),
        UniqueConstraint("shipping_method_id", "emirate", name="uq_shipping_rates_method_emirate"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    shipping_method_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("shipping_methods.id", ondelete="CASCADE"), nullable=False
    )
    emirate: Mapped[str] = mapped_column(String(20), nullable=False)
    rate_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    free_shipping_min_order_amount: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    shipping_method: Mapped["ShippingMethod"] = relationship(back_populates="rates")
