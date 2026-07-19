"""`inventory` — stock tracking, one row per variant (database-schema.md, 5.7).

Note this entity has only `updated_at`, no `created_at`, per the schema doc.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_quantity_on_hand_nonneg"),
        CheckConstraint("quantity_reserved >= 0", name="ck_inventory_quantity_reserved_nonneg"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    quantity_on_hand: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    quantity_reserved: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    low_stock_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("5")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    variant: Mapped["ProductVariant"] = relationship(back_populates="inventory")
