"""`product_media` — images and videos in a single ordered gallery per product,
optionally scoped to a variant (database-schema.md, 5.6).
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    false,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.product_variant import ProductVariant


class ProductMedia(CreatedAtMixin, Base):
    __tablename__ = "product_media"
    __table_args__ = (
        CheckConstraint("media_type IN ('image', 'video')", name="ck_product_media_media_type"),
        Index("ix_product_media_product_id_sort_order", "product_id", "sort_order"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    product_variant_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alt_text_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    alt_text_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=false())

    product: Mapped["Product"] = relationship(back_populates="media")
    variant: Mapped["ProductVariant | None"] = relationship(back_populates="media")
