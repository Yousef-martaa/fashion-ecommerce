"""`homepage_sections` — admin-manageable, reorderable homepage content blocks
(database-schema.md, 5.20). Standalone: no foreign keys in or out (decision 20).
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Index,
    Integer,
    String,
    Text,
    text,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class HomepageSection(TimestampMixin, Base):
    __tablename__ = "homepage_sections"
    __table_args__ = (
        CheckConstraint(
            "section_type IN ('hero', 'collections', 'featured_products', 'offers', "
            "'banner', 'brand_story', 'custom_block')",
            name="ck_homepage_sections_section_type",
        ),
        CheckConstraint(
            "media_type IN ('image', 'video')", name="ck_homepage_sections_media_type"
        ),
        Index("ix_homepage_sections_is_active_display_order", "is_active", "display_order"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    section_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
