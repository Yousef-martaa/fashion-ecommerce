"""`users` — registered customer accounts (database-schema.md, 5.1)."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String, false, text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.cart import Cart
    from app.models.coupon import CouponRedemption
    from app.models.order import Order
    from app.models.wishlist import Wishlist


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    preferred_language: Mapped[str] = mapped_column(
        String(2), nullable=False, server_default=text("'en'")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=false())

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    carts: Mapped[list["Cart"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    coupon_redemptions: Mapped[list["CouponRedemption"]] = relationship(back_populates="user")
    wishlist: Mapped["Wishlist | None"] = relationship(back_populates="user")
