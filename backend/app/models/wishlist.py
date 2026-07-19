"""`wishlists` and `wishlist_items` (database-schema.md, 5.18-5.19).

FUTURE SCOPE ONLY. These tables are modeled for forward compatibility so the
schema doesn't need a breaking change when the feature ships (decision 13).
No wishlist API, UI, or business logic exists yet, and none should be added
against these models as part of this task.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant
    from app.models.user import User


class Wishlist(CreatedAtMixin, Base):
    """Future scope — not part of the MVP. See module docstring."""

    __tablename__ = "wishlists"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="wishlist")
    items: Mapped[list["WishlistItem"]] = relationship(
        back_populates="wishlist", cascade="all, delete-orphan", passive_deletes=True
    )


class WishlistItem(CreatedAtMixin, Base):
    """Future scope — not part of the MVP. See module docstring."""

    __tablename__ = "wishlist_items"
    __table_args__ = (
        UniqueConstraint(
            "wishlist_id", "product_variant_id", name="uq_wishlist_items_wishlist_variant"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wishlist_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False
    )
    product_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    wishlist: Mapped["Wishlist"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="wishlist_items")
