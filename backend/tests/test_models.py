"""Tests that the SQLAlchemy model metadata matches docs/database-schema.md.

These tests introspect `Base.metadata` directly -- no database connection is
required or used.
"""

from sqlalchemy import CheckConstraint

from app.models import Base

EXPECTED_TABLES = {
    "users",
    "addresses",
    "categories",
    "products",
    "product_variants",
    "product_media",
    "inventory",
    "shipping_methods",
    "shipping_rates",
    "carts",
    "cart_items",
    "coupons",
    "coupon_redemptions",
    "orders",
    "order_addresses",
    "order_items",
    "payments",
    "wishlists",
    "wishlist_items",
    "homepage_sections",
}

FUTURE_SCOPE_TABLES = {"wishlists", "wishlist_items"}

EMIRATES = (
    "Abu Dhabi",
    "Dubai",
    "Sharjah",
    "Ajman",
    "Umm Al Quwain",
    "Ras Al Khaimah",
    "Fujairah",
)


def test_all_expected_tables_are_registered():
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_entity_count_matches_schema_doc():
    # docs/database-schema.md section 9: "20 entities in total".
    assert len(Base.metadata.tables) == 20


def test_no_duplicate_columns_within_any_table():
    for name, table in Base.metadata.tables.items():
        column_names = [c.name for c in table.columns]
        assert len(column_names) == len(set(column_names)), f"duplicate column in {name}"


def test_every_table_has_a_single_surrogate_integer_primary_key():
    for name, table in Base.metadata.tables.items():
        pk_columns = list(table.primary_key.columns)
        assert len(pk_columns) == 1, f"{name} should have exactly one PK column"
        assert pk_columns[0].name == "id", f"{name} PK should be named 'id'"


def test_created_at_present_everywhere_updated_at_only_where_documented():
    # database-schema.md 5.7 (inventory) and 5.13 (coupon_redemptions) are the
    # two documented exceptions that do not follow the created_at/updated_at
    # pair used by every other entity.
    no_created_at = {"inventory", "coupon_redemptions"}
    no_updated_at = {
        "product_media",
        "order_addresses",
        "order_items",
        "wishlists",
        "wishlist_items",
        "coupon_redemptions",
        "inventory",
    }
    for name, table in Base.metadata.tables.items():
        if name not in no_created_at:
            assert "created_at" in table.columns, f"{name} missing created_at"
        if name not in no_updated_at:
            assert "updated_at" in table.columns, f"{name} missing updated_at"


def test_currency_columns_default_to_aed():
    for table_name in ("carts", "orders", "payments"):
        column = Base.metadata.tables[table_name].columns["currency"]
        assert column.server_default is not None
        assert "AED" in str(column.server_default.arg)


def test_monetary_columns_are_numeric_10_2():
    numeric_columns = [
        ("products", "base_price"),
        ("product_variants", "price"),
        ("product_variants", "compare_at_price"),
        ("coupons", "discount_value"),
        ("coupons", "min_order_amount"),
        ("shipping_rates", "rate_amount"),
        ("shipping_rates", "free_shipping_min_order_amount"),
        ("orders", "subtotal"),
        ("orders", "discount_amount"),
        ("orders", "shipping_amount"),
        ("orders", "tax_amount"),
        ("orders", "total_amount"),
        ("order_items", "unit_price"),
        ("order_items", "line_total"),
        ("payments", "amount"),
        ("coupon_redemptions", "discount_amount"),
    ]
    for table_name, column_name in numeric_columns:
        column = Base.metadata.tables[table_name].columns[column_name]
        assert column.type.precision == 10, f"{table_name}.{column_name} precision"
        assert column.type.scale == 2, f"{table_name}.{column_name} scale"


def test_emirate_check_constraint_present_on_uae_address_tables():
    for table_name in ("addresses", "order_addresses", "shipping_rates"):
        table = Base.metadata.tables[table_name]
        check_texts = [
            str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)
        ]
        assert any(
            all(emirate in text for emirate in EMIRATES) for text in check_texts
        ), f"{table_name} missing the 7-emirate CHECK constraint"


def test_enum_like_fields_have_check_constraints_only_where_the_doc_specifies():
    # Per docs/database-schema.md, these columns get an explicit CHECK ...
    expected_checked = {
        ("products", "status"),
        ("product_media", "media_type"),
        ("coupons", "discount_type"),
        ("order_addresses", "address_type"),
        ("payments", "method"),
        ("homepage_sections", "section_type"),
        ("homepage_sections", "media_type"),
    }
    # ... while these are deliberately left without one (descriptive notes only).
    expected_unchecked = {
        ("users", "preferred_language"),
        ("orders", "status"),
        ("orders", "payment_status"),
        ("payments", "status"),
    }

    def checked_columns(table_name: str) -> set[str]:
        table = Base.metadata.tables[table_name]
        columns: set[str] = set()
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint):
                text = str(constraint.sqltext)
                for column in table.columns:
                    if f"{column.name} IN" in text:
                        columns.add(column.name)
        return columns

    for table_name, column_name in expected_checked:
        assert column_name in checked_columns(table_name), (
            f"{table_name}.{column_name} should have a CHECK constraint"
        )
    for table_name, column_name in expected_unchecked:
        assert column_name not in checked_columns(table_name), (
            f"{table_name}.{column_name} should NOT have a CHECK constraint"
        )


def test_key_foreign_key_ondelete_behaviors():
    cases = [
        ("addresses", "user_id", "CASCADE"),
        ("categories", "parent_id", "RESTRICT"),
        ("products", "category_id", "RESTRICT"),
        ("product_variants", "product_id", "CASCADE"),
        ("product_media", "product_id", "CASCADE"),
        ("product_media", "product_variant_id", "CASCADE"),
        ("inventory", "product_variant_id", "CASCADE"),
        ("carts", "user_id", "CASCADE"),
        ("cart_items", "cart_id", "CASCADE"),
        ("cart_items", "product_variant_id", "CASCADE"),
        ("shipping_rates", "shipping_method_id", "CASCADE"),
        ("coupon_redemptions", "coupon_id", "CASCADE"),
        ("coupon_redemptions", "user_id", "CASCADE"),
        ("coupon_redemptions", "order_id", "CASCADE"),
        ("orders", "user_id", "SET NULL"),
        ("orders", "coupon_id", "SET NULL"),
        ("orders", "shipping_method_id", "SET NULL"),
        ("order_addresses", "order_id", "CASCADE"),
        ("order_addresses", "address_id", "SET NULL"),
        ("order_items", "order_id", "CASCADE"),
        ("order_items", "product_variant_id", "SET NULL"),
        ("payments", "order_id", "CASCADE"),
        ("wishlists", "user_id", "CASCADE"),
        ("wishlist_items", "wishlist_id", "CASCADE"),
        ("wishlist_items", "product_variant_id", "CASCADE"),
    ]
    for table_name, column_name, expected_ondelete in cases:
        table = Base.metadata.tables[table_name]
        fks = list(table.columns[column_name].foreign_keys)
        assert fks, f"{table_name}.{column_name} should have a foreign key"
        assert fks[0].ondelete == expected_ondelete, (
            f"{table_name}.{column_name} ondelete should be {expected_ondelete}, "
            f"got {fks[0].ondelete}"
        )


def test_unique_constraints_present():
    def unique_column_sets(table_name: str) -> list[set[str]]:
        table = Base.metadata.tables[table_name]
        sets = [
            {c.name for c in uc.columns}
            for uc in table.constraints
            if uc.__class__.__name__ == "UniqueConstraint"
        ]
        for idx in table.indexes:
            if idx.unique:
                sets.append({c.name for c in idx.columns})
        for column in table.columns:
            if column.unique:
                sets.append({column.name})
        return sets

    cases = [
        ("users", {"email"}),
        ("categories", {"slug"}),
        ("products", {"slug"}),
        ("product_variants", {"sku"}),
        ("product_variants", {"product_id", "size", "color_name_en"}),
        ("inventory", {"product_variant_id"}),
        ("carts", {"guest_token"}),
        ("cart_items", {"cart_id", "product_variant_id"}),
        ("coupons", {"code"}),
        ("coupon_redemptions", {"coupon_id", "user_id"}),
        ("shipping_methods", {"code"}),
        ("shipping_rates", {"shipping_method_id", "emirate"}),
        ("orders", {"order_number"}),
        ("order_addresses", {"order_id", "address_type"}),
        ("wishlists", {"user_id"}),
        ("wishlist_items", {"wishlist_id", "product_variant_id"}),
    ]
    for table_name, expected_columns in cases:
        assert expected_columns in unique_column_sets(table_name), (
            f"{table_name} missing UNIQUE on {expected_columns}"
        )


def test_wishlist_tables_are_isolated_future_scope():
    # No non-wishlist table should reference the wishlist tables: wishlists
    # must stay a bolt-on that nothing else in the MVP schema depends on.
    for name, table in Base.metadata.tables.items():
        if name in FUTURE_SCOPE_TABLES:
            continue
        for fk in table.foreign_keys:
            assert fk.column.table.name not in FUTURE_SCOPE_TABLES, (
                f"{name} references future-scope table {fk.column.table.name}"
            )


def test_homepage_sections_config_is_jsonb_with_empty_object_default():
    table = Base.metadata.tables["homepage_sections"]
    column = table.columns["config"]
    assert column.type.__class__.__name__ == "JSONB"
    assert column.server_default is not None


def test_no_brand_column_on_products():
    # decision: single-brand store, not a marketplace -- see docs/database-schema.md.
    assert "brand" not in Base.metadata.tables["products"].columns


def test_products_status_replaces_boolean_is_active():
    products = Base.metadata.tables["products"]
    assert "status" in products.columns
    assert "is_active" not in products.columns


def test_product_variants_keep_boolean_is_active():
    variants = Base.metadata.tables["product_variants"]
    assert "is_active" in variants.columns
    assert "status" not in variants.columns
