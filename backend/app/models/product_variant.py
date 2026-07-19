"""`product_variants` — the sellable/stockable unit: one size+color of a product
(database-schema.md, 5.5).
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cart import CartItem
    from app.models.inventory import Inventory
    from app.models.order import OrderItem
    from app.models.product import Product
    from app.models.product_media import ProductMedia
    from app.models.wishlist import WishlistItem


class ProductVariant(TimestampMixin, Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "size", "color_name_en", name="uq_product_variants_product_size_color"
        ),
        Index("ix_product_variants_product_id_is_active", "product_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    color_name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    color_name_ar: Mapped[str] = mapped_column(String(50), nullable=False)
    color_hex: Mapped[str | None] = mapped_column(CHAR(7), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    compare_at_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    weight_grams: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    product: Mapped["Product"] = relationship(back_populates="variants")
    media: Mapped[list["ProductMedia"]] = relationship(
        back_populates="variant", cascade="all, delete-orphan", passive_deletes=True
    )
    inventory: Mapped["Inventory | None"] = relationship(
        back_populates="variant", cascade="all, delete-orphan", passive_deletes=True, uselist=False
    )
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="variant")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="variant")
    wishlist_items: Mapped[list["WishlistItem"]] = relationship(back_populates="variant")
