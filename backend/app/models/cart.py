"""`carts` and `cart_items` — ephemeral, hard-deleted, not snapshotted
(database-schema.md, 5.10-5.11).
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CHAR,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant
    from app.models.user import User


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"
    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR guest_token IS NOT NULL", name="ck_carts_user_or_guest"
        ),
        Index(
            "ux_carts_guest_token",
            "guest_token",
            unique=True,
            postgresql_where=text("guest_token IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    guest_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, server_default=text("'AED'"))

    user: Mapped["User | None"] = relationship(back_populates="carts")
    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan", passive_deletes=True
    )


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_variant_id", name="uq_cart_items_cart_variant"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cart_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False
    )
    product_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="cart_items")
