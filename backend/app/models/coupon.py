"""`coupons` and `coupon_redemptions` (database-schema.md, 5.12-5.13).

`coupon_redemptions` is the per-user/per-contact enforcement ledger that makes
account- and first-order-restricted coupons (e.g. the signup discount) actually
enforceable — a global `usage_count` alone cannot do this (decision 10).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.user import User


class Coupon(TimestampMixin, Base):
    __tablename__ = "coupons"
    __table_args__ = (
        CheckConstraint(
            "discount_type IN ('percentage', 'fixed')", name="ck_coupons_discount_type"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    discount_type: Mapped[str] = mapped_column(String(10), nullable=False)
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_order_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_discount_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    requires_account: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    first_order_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    max_redemptions_per_user: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("1")
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    orders: Mapped[list["Order"]] = relationship(back_populates="coupon")
    redemptions: Mapped[list["CouponRedemption"]] = relationship(
        back_populates="coupon", cascade="all, delete-orphan", passive_deletes=True
    )


class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"
    __table_args__ = (
        Index(
            "ux_coupon_redemptions_coupon_user",
            "coupon_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index("ix_coupon_redemptions_coupon_id", "coupon_id"),
        Index("ix_coupon_redemptions_email", "email"),
        Index("ix_coupon_redemptions_phone", "phone"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    coupon_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    coupon: Mapped["Coupon"] = relationship(back_populates="redemptions")
    user: Mapped["User | None"] = relationship(back_populates="coupon_redemptions")
    order: Mapped["Order"] = relationship(back_populates="coupon_redemptions")
