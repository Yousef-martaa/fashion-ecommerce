"""`orders`, `order_addresses`, `order_items` (database-schema.md, 5.14-5.16).

Placing an order snapshots everything it shows the customer: line items,
addresses, and the chosen shipping method (decisions 4, 8, 11).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, TimestampMixin, emirate_check

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.coupon import Coupon, CouponRedemption
    from app.models.payment import Payment
    from app.models.product_variant import ProductVariant
    from app.models.shipping import ShippingMethod
    from app.models.user import User


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR guest_email IS NOT NULL", name="ck_orders_user_or_guest"
        ),
        Index("ix_orders_user_id_created_at", "user_id", text("created_at DESC")),
        Index("ix_orders_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'unpaid'")
    )
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, server_default=text("'AED'"))
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0")
    )
    coupon_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    shipping_method_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("shipping_methods.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipping_method_name_en: Mapped[str] = mapped_column(String(150), nullable=False)
    shipping_method_name_ar: Mapped[str] = mapped_column(String(150), nullable=False)
    shipping_estimated_days_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipping_estimated_days_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipping_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0")
    )
    tax_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0")
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User | None"] = relationship(back_populates="orders")
    coupon: Mapped["Coupon | None"] = relationship(back_populates="orders")
    shipping_method: Mapped["ShippingMethod | None"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )
    addresses: Mapped[list["OrderAddress"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )
    coupon_redemptions: Mapped[list["CouponRedemption"]] = relationship(back_populates="order")


class OrderAddress(CreatedAtMixin, Base):
    __tablename__ = "order_addresses"
    __table_args__ = (
        CheckConstraint(
            "address_type IN ('shipping', 'billing')", name="ck_order_addresses_address_type"
        ),
        CheckConstraint(emirate_check(), name="ck_order_addresses_emirate"),
        UniqueConstraint("order_id", "address_type", name="uq_order_addresses_order_type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    address_type: Mapped[str] = mapped_column(String(10), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    emirate: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=False)
    apartment_or_villa_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    landmark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="addresses")
    address: Mapped["Address | None"] = relationship(back_populates="order_addresses")


class OrderItem(CreatedAtMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_variant_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    variant_attributes: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant | None"] = relationship(back_populates="order_items")
