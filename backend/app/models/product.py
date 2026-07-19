"""`products` — catalog-level product; not directly sellable (database-schema.md, 5.4).

See `product_variants` for the actual sellable/stockable unit.
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.product_media import ProductMedia
    from app.models.product_variant import ProductVariant


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')", name="ck_products_status"
        ),
        Index("ix_products_status_category_id", "status", "category_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(280), unique=True, nullable=False)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description_en: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta_description_ar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default=text("'draft'")
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", passive_deletes=True
    )
    media: Mapped[list["ProductMedia"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", passive_deletes=True
    )
