"""SQLAlchemy models package.

Every model must be imported here so it registers on `Base.metadata` — this is
what lets Alembic (see alembic/env.py: `target_metadata = Base.metadata`)
discover the complete schema for autogeneration and validation.

Import order follows the entities' foreign-key dependency order, matching
docs/database-schema.md section 5.
"""

from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.shipping import ShippingMethod, ShippingRate
from app.models.coupon import Coupon, CouponRedemption
from app.models.address import Address
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_media import ProductMedia
from app.models.inventory import Inventory
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderAddress, OrderItem
from app.models.payment import Payment
from app.models.wishlist import Wishlist, WishlistItem
from app.models.homepage_section import HomepageSection

__all__ = [
    "Base",
    "User",
    "Category",
    "ShippingMethod",
    "ShippingRate",
    "Coupon",
    "CouponRedemption",
    "Address",
    "Product",
    "ProductVariant",
    "ProductMedia",
    "Inventory",
    "Cart",
    "CartItem",
    "Order",
    "OrderAddress",
    "OrderItem",
    "Payment",
    "Wishlist",
    "WishlistItem",
    "HomepageSection",
]
