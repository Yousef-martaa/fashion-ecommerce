# Database Schema Design

Status: design only. No SQLAlchemy models or Alembic migrations exist yet — this document is the reference used to build them.

Target database: PostgreSQL 16+.
Market: United Arab Emirates only (single country, single currency).

## 1. Scope and requirements

The schema below supports:

- Guest checkout (no account required) alongside registered-user accounts
- A product catalog with categories limited to two levels for the MVP (category → subcategory)
- Product variants by size and color, each with its own SKU, price, and stock
- Product media — images and videos together in a single ordered gallery per product, optionally per variant
- Bilingual (Arabic/English) content across catalog, shipping, and homepage text
- SEO metadata (meta title/description, bilingual) for products and categories
- Inventory tracking at the variant level
- Shopping carts for both guests (session-based) and registered users
- Orders and order line items, decoupled from the live catalog through snapshotting
- UAE-only addresses — emirate-based, no country selector — reusable per user and one-off for guests
- Shipping methods and emirate-specific shipping rates, including free-shipping thresholds, snapshotted onto each order
- Payments supporting multiple attempts per order, provider-neutral: card, Apple Pay, Google Pay, cash on delivery today; Tabby and Tamara as later additions
- Coupons/discount codes, including a 10%-off-first-order promotion for registered users with per-account abuse prevention
- A wishlist, modeled for future support only — no wishlist API, UI, or business logic ships in the MVP
- Homepage content management (hero, collections, featured products, offers, banners, brand story, custom blocks) so admins can manage and reorder homepage sections without code changes
- AED as the sole currency across carts, orders, and payments

Out of scope for this document: reviews/ratings, a returns/refunds workflow, VAT/tax-rate tables, analytics/reporting tables, and admin/staff roles and permissions. These can be added later without disrupting the entities below.

## 2. Design decisions

1. **Bilingual content is columns, not tables.** Every customer-facing text field gets sibling `_en`/`_ar` columns (e.g. `name_en`, `name_ar`) rather than a normalized `translations` table. The platform needs exactly two fixed locales, so a join for every text lookup would add cost with no benefit. If a third language is ever needed, more columns can be added; only if locales become open-ended would a translation table be worth the join overhead.

2. **Guests are first-class, not shadow users.** `carts`, `addresses`, and `orders` all accept a nullable `user_id`, and `orders` additionally snapshots contact details (email, phone) directly onto the row. Guest checkout never requires creating a placeholder user account, and a guest order remains fully readable even if that guest never registers.

3. **Variants, not products, are the sellable unit.** `products` holds shared catalog data — name, description, category, base price, media, SEO. `product_variants` holds the size/color combination, SKU, and price override, and is what `inventory`, `cart_items`, and `order_items` actually reference. This matches how fashion retail works physically and avoids one near-duplicate "product" per color.

4. **Order items snapshot everything they show the customer.** `order_items` copies `product_name_en/ar`, `unit_price`, and a rendered `variant_attributes` string at the moment of purchase, rather than joining live to the catalog. A later rename, repricing, or deletion of the product must never change what a past order displays.

5. **Order-to-catalog references are soft, not hard-cascaded.** `order_items.product_variant_id` is a nullable foreign key with `ON DELETE SET NULL`. Deleting a variant must never delete or corrupt an order; the snapshot fields from decision 4 keep the line item fully readable even once the link is gone.

6. **Inventory is its own table, not columns on the variant.** Stock counts and reservations are a high-write, contention-heavy concern; variant metadata (size, color, price) is low-write and high-read. Separating them avoids lock contention on browsing traffic and leaves room for per-warehouse stock later without touching `product_variants`.

7. **Addresses are UAE-only and emirate-based — there is no `country` column.** The store ships exclusively within the UAE, so a country selector would be pure friction. Every address instead carries an `emirate` value drawn from the fixed set of seven emirates: Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah. Because that set is small, fixed, and effectively permanent, it is enforced with a `CHECK` constraint (a native Postgres `ENUM` type would work equally well) rather than a separate lookup table. `postal_code` is kept but optional, since UAE addressing is landmark/area-driven rather than postal-code-driven.

8. **Addresses are reusable; orders snapshot them.** A user can store multiple `addresses`. At checkout, the shipping and billing address are copied onto the order (`order_addresses`, one row per `address_type`) so that editing or deleting a saved address afterward never rewrites history. A guest's address is written straight into `order_addresses` with `address_id` left `NULL` — there is nothing to reuse.

9. **Coupons are rules; orders record outcomes.** `coupons` holds the reusable rule (percentage or fixed, minimum order amount, expiry, usage limits, account/first-order restrictions). `orders` stores a nullable `coupon_id` (`ON DELETE SET NULL`) plus the `discount_amount` actually applied, so a past order still shows its discount even if the coupon is later edited or deleted.

10. **The first-order signup discount needs a redemption ledger, not just `coupons.usage_count`.** A single global counter cannot answer "has this specific user already redeemed this," nor can it flag the same person redeeming again under a second account using the same email or phone. `coupon_redemptions` — one row per successful redemption, carrying `user_id` plus a snapshotted `email`/`phone` and the `order_id` — provides that per-user, per-contact, auditable trail. See entity 5.13.

11. **The shipping method is snapshotted as columns on `orders`, not a child table.** Unlike addresses, which need two rows per order (shipping and billing), an order has exactly one shipping method — so it follows the same pattern already used for coupons: a nullable `shipping_method_id` (`ON DELETE SET NULL`) plus snapshotted name and delivery-estimate columns, with no extra table required.

12. **Payments are their own table (one-to-many) and provider-neutral.** An order can accumulate more than one payment attempt — a decline, a retry, a partial capture — so `payments` references `order_id` rather than living as columns on `orders`. `provider` and `method` are UAE-relevant and vendor-neutral: card gateways such as Network International, Telr, or PayTabs; Apple Pay; Google Pay; cash on delivery; with Tabby and Tamara reserved as buy-now-pay-later additions. `orders.payment_status` stays a derived summary field for fast filtering.

13. **Wishlist is modeled now, shipped later.** `wishlists` and `wishlist_items` exist purely so the schema doesn't need a breaking change when the feature is greenlit. Registered users only — a wishlist has no meaning without a persistent identity. No API, UI, or business logic against these tables is part of the current MVP.

14. **Category depth is capped at two levels by application logic, not by the schema.** `categories` keeps a single self-referencing `parent_id` rather than two separate `categories`/`subcategories` tables, because one self-referencing table costs nothing extra and stays flexible. For the MVP, the application rejects setting a `parent_id` on any category whose own `parent_id` is already non-null — enforcing exactly category → subcategory. Nothing in the schema itself prevents deeper nesting, so lifting the limit later is an application change, not a migration.

15. **Product media is one table for images and videos, ordered as a single gallery.** `media_type` discriminates `image` from `video`; both share the same ordering, primary-flag, and product/variant scoping, so one table with a type column is simpler than maintaining parallel image and video tables — and it lets the storefront render one continuous, navigable gallery mixing both media types by `sort_order`, rather than a separate image carousel and video section.

16. **SEO fields live directly on `products` and `categories`.** Each product or category has exactly one SEO record, so normalizing meta title/description into a child table would only add a join for no benefit — the same reasoning as decision 1. Categories get the same SEO fields as products because category pages are commonly-indexed storefront landing pages in their own right (e.g. "Men's Shirts – UAE"), not just containers that inherit a parent's metadata.

17. **`products.status` replaces a boolean; `product_variants.is_active` stays a boolean — deliberately different shapes.** A product's lifecycle needs a third state a boolean can't express: being authored but not yet public (`draft`), live (`published`), and discontinued-but-retained-for-history (`archived`) — see entity 5.4. A variant only ever needs one yes/no fact — is this specific size/color currently purchasable — independent of whether the parent product is published, so a boolean remains sufficient there.

18. **Soft delete for catalog data; hard delete for ephemeral data.** `categories` and `product_variants` use `is_active`; `products` uses `status` (decision 17). None of these rows are ever physically deleted, since historical orders and carts may still reference them. Carts and cart items, having no historical value once abandoned or converted, are hard-deleted.

19. **Shipping rates vary by emirate, on a table separate from shipping methods.** `shipping_methods` describes the reusable method (standard, express, free) and its delivery-time estimate; `shipping_rates` holds the actual price per method per emirate, plus an optional free-shipping subtotal threshold. Splitting these lets "Standard" cost something different in Fujairah than in Dubai, and lets a free-shipping threshold be defined once per method/emirate pair instead of duplicated per method.

20. **Homepage content is one generic table with a JSONB configuration column, not one table per section type.** `homepage_sections` has typed columns for what every section shares — bilingual title/content, media, ordering, active flag — and a single `config` JSONB column for whatever varies by `section_type` (which category IDs a "collections" section shows, a CTA link on a "hero" section, and so on). New section types, or new options on existing ones, never require a migration. The trade-off is that IDs referenced inside `config` are not foreign-key enforced; this is tracked as an open question in section 8.

21. **Surrogate integer primary keys everywhere; natural keys as unique constraints.** Every table uses `id BIGSERIAL PRIMARY KEY`. Business-meaningful values — `sku`, `email`, `coupons.code`, `shipping_methods.code` — get `UNIQUE` constraints instead of serving as the primary key, so joins stay cheap and a business key can still change if it ever needs to.

22. **Timestamps on every table.** `created_at`/`updated_at` (`TIMESTAMPTZ`, default `now()`) support auditing, sorting, and future analytics.

23. **Money is `NUMERIC(10,2)`, never floating point, denominated in AED.** Fixed-point arithmetic avoids rounding drift in prices, totals, and discounts. `currency` columns are still kept on `carts`, `orders`, and `payments` (default `'AED'`) so multi-currency support could be added later without a schema change — not because multi-currency is in scope now.

## 3. ERD overview

**Core commerce:**

```
                                   ┌───────────────┐
                                   │     users     │
                                   └───────┬───────┘
                    ┌───────────────┬──────┼───────────────┬───────────────┐
                    │               │      │               │               │
              ┌─────▼─────┐   ┌─────▼────┐ │        ┌──────▼──────┐  ┌─────▼─────┐
              │ addresses │   │  carts   │ │        │  wishlists  │  │  orders   │
              │(UAE emirate)│ └────┬─────┘ │        │  (future)   │  └─────┬─────┘
              └─────┬─────┘        │       │         └──────┬──────┘       │
                    │        ┌─────▼─────┐ │        ┌───────▼──────┐       │
                    │        │cart_items │ │        │wishlist_items│       │
                    │        └─────┬─────┘ │        │   (future)   │       │
                    │              │       │         └──────────────┘      │
         (snapshot) │              │       │                        ┌──────┴───────┐
                    │              │       │                        │              │
              ┌─────▼──────┐       │       │                 ┌──────▼─────┐ ┌──────▼──────┐
              │order_addr. │       │       │                 │order_items │ │  payments   │
              │(UAE emirate)│      │       │                 └──────┬─────┘ └─────────────┘
              └────────────┘       │       │                        │
                                    │       │                 ┌──────▼───────────┐
                                    └───────┼─────────────────┤ product_variants  │
                                            │                 └─────────┬─────────┘
                                            │           ┌────────────────┼────────────────┐
                                            │     ┌─────▼─────┐  ┌───────▼──────┐  ┌───────▼──────┐
                                            │     │ inventory │  │   products   │  │ product_media │
                                            │     └───────────┘  │(status, SEO) │  │ (image/video, │
                                            │                     └──────┬───────┘  │  one gallery) │
                                            │                     ┌──────▼──────┐   └───────────────┘
                                            │                     │ categories  │
                                            │                     │(2 levels,   │
                                            │                     │    SEO)     │
                                            │                     └─────────────┘
                                            │
                              ┌─────────────▼────────┐        ┌─────────────────────┐
                              │  shipping_methods     │        │       coupons       │
                              │  → shipping_rates     │        │ (incl. signup       │
                              │  (snapshotted onto    │        │  discount rule)     │
                              │   orders, decision 11)│        └──────────┬──────────┘
                              └───────────────────────┘                   │
                                                                    ┌──────▼────────────┐
                                                                    │ coupon_redemptions │
                                                                    │  → users, orders   │
                                                                    │   (decision 10)    │
                                                                    └────────────────────┘
```

**Homepage content (standalone — no foreign keys in or out):**

```
┌────────────────────────────────────────────────┐
│                homepage_sections                │
│  section_type · title_en/ar · content_en/ar     │
│  media_url/type · config (JSONB) · display_order│
│  is_active · created_at/updated_at              │
└────────────────────────────────────────────────┘
```

## 4. Cardinality summary

| Relationship | Cardinality |
|---|---|
| users → addresses | 1 : N |
| users → carts | 1 : N (typically 0 or 1 active) |
| users → orders | 1 : N |
| users → coupon_redemptions | 1 : N |
| users → wishlists (future) | 1 : 1 |
| categories → categories (parent → subcategory) | 1 : N, self-referencing, app-capped at 2 levels |
| categories → products | 1 : N |
| products → product_variants | 1 : N |
| products → product_media | 1 : N |
| product_variants → product_media | 1 : N, optional, variant-scoped |
| product_variants → inventory | 1 : 1 |
| carts → cart_items | 1 : N |
| cart_items → product_variants | N : 1 |
| coupons → orders | 1 : N |
| coupons → coupon_redemptions | 1 : N |
| coupon_redemptions → orders | N : 1 |
| shipping_methods → shipping_rates | 1 : N |
| shipping_methods → orders | 1 : N, snapshotted, nullable FK |
| orders → order_items | 1 : N |
| orders → payments | 1 : N |
| orders → order_addresses | 1 : 2 (shipping + billing) |
| order_items → product_variants | N : 1, nullable, `SET NULL` |
| wishlists → wishlist_items (future) | 1 : N |
| wishlist_items → product_variants (future) | N : 1 |
| homepage_sections → (none) | standalone; any product/category IDs live only inside `config` JSONB, unenforced |

## 5. Entities

### 5.1 `users`

Registered customer accounts. Guests never get a row here.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `email` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` | Login identifier |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Hashed (bcrypt/argon2) |
| `first_name` | `VARCHAR(100)` | `NOT NULL` | |
| `last_name` | `VARCHAR(100)` | `NOT NULL` | |
| `phone` | `VARCHAR(30)` | nullable | E.164 recommended |
| `preferred_language` | `VARCHAR(2)` | `NOT NULL`, default `'en'` | `'en'` or `'ar'` |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | Account enabled/disabled |
| `is_verified` | `BOOLEAN` | `NOT NULL`, default `false` | Email verification |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: has many `addresses`, `orders`, `coupon_redemptions`, and historically `carts`; has one `wishlist` (future scope).

### 5.2 `addresses`

Shipping/billing addresses within the UAE. Reusable by registered users; a single-use row for guests.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE CASCADE`, nullable | Null for a guest-only address |
| `label` | `VARCHAR(50)` | nullable | e.g. "Home", "Work" |
| `full_name` | `VARCHAR(200)` | `NOT NULL` | Recipient name |
| `phone` | `VARCHAR(30)` | `NOT NULL` | |
| `emirate` | `VARCHAR(20)` | `NOT NULL`, `CHECK (emirate IN ('Abu Dhabi','Dubai','Sharjah','Ajman','Umm Al Quwain','Ras Al Khaimah','Fujairah'))` | See decision 7 |
| `city` | `VARCHAR(100)` | nullable | Mainly relevant for Abu Dhabi emirate (e.g. Al Ain); optional elsewhere |
| `area` | `VARCHAR(100)` | `NOT NULL` | District/community — the primary UAE locator |
| `street` | `VARCHAR(255)` | `NOT NULL` | |
| `building` | `VARCHAR(100)` | `NOT NULL` | Building/villa name or number |
| `apartment_or_villa_no` | `VARCHAR(50)` | nullable | |
| `landmark` | `VARCHAR(255)` | nullable | Nearby landmark, commonly used for UAE delivery |
| `postal_code` | `VARCHAR(20)` | nullable | Optional — not central to UAE addressing |
| `is_default` | `BOOLEAN` | `NOT NULL`, default `false` | Default address for the user |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: optionally belongs to a `user`; copied into `order_addresses` at checkout.

### 5.3 `categories`

Two-level category tree for the MVP (category → subcategory). Bilingual, with SEO metadata.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `parent_id` | `BIGINT` | FK → `categories.id`, `ON DELETE RESTRICT`, nullable | Null = top-level; app rejects a parent that itself has a parent (decision 14) |
| `name_en` | `VARCHAR(150)` | `NOT NULL` | |
| `name_ar` | `VARCHAR(150)` | `NOT NULL` | |
| `slug` | `VARCHAR(160)` | `UNIQUE`, `NOT NULL` | |
| `description_en` | `TEXT` | nullable | |
| `description_ar` | `TEXT` | nullable | |
| `meta_title_en` | `VARCHAR(255)` | nullable | SEO — decision 16 |
| `meta_title_ar` | `VARCHAR(255)` | nullable | |
| `meta_description_en` | `VARCHAR(500)` | nullable | |
| `meta_description_ar` | `VARCHAR(500)` | nullable | |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | Soft delete/hide |
| `sort_order` | `INTEGER` | `NOT NULL`, default `0` | Display ordering |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: self-referencing parent/subcategory, capped at two levels by application logic; has many `products`. `ON DELETE RESTRICT` blocks deleting a category that still has subcategories.

### 5.4 `products`

Catalog-level product; not directly sellable — see `product_variants`. Bilingual, with SEO metadata and a lifecycle `status`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `category_id` | `BIGINT` | FK → `categories.id`, `ON DELETE RESTRICT`, `NOT NULL` | |
| `name_en` | `VARCHAR(255)` | `NOT NULL` | |
| `name_ar` | `VARCHAR(255)` | `NOT NULL` | |
| `slug` | `VARCHAR(280)` | `UNIQUE`, `NOT NULL` | |
| `description_en` | `TEXT` | nullable | |
| `description_ar` | `TEXT` | nullable | |
| `meta_title_en` | `VARCHAR(255)` | nullable | SEO — decision 16 |
| `meta_title_ar` | `VARCHAR(255)` | nullable | |
| `meta_description_en` | `VARCHAR(500)` | nullable | |
| `meta_description_ar` | `VARCHAR(500)` | nullable | |
| `base_price` | `NUMERIC(10,2)` | `NOT NULL` | Reference price in AED; variants may override |
| `status` | `VARCHAR(10)` | `NOT NULL`, default `'draft'`, `CHECK (status IN ('draft','published','archived'))` | Decision 17 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

`status` values:
- `draft` — being authored; hidden from browsing, search, and category listings.
- `published` — live; individually purchasable subject to `product_variants.is_active` and available stock.
- `archived` — discontinued and hidden from browsing/search, but never deleted, so historical `order_items` that reference it stay fully resolvable.

There is no `brand` column — this is a single-brand store, not a marketplace.

Relationships: belongs to one `category`; has many `product_variants` and `product_media`.

### 5.5 `product_variants`

The sellable/stockable unit: one size + color combination of a product.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `product_id` | `BIGINT` | FK → `products.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `sku` | `VARCHAR(64)` | `UNIQUE`, `NOT NULL` | |
| `size` | `VARCHAR(20)` | `NOT NULL` | e.g. `S`, `M`, `L`, `42` |
| `color_name_en` | `VARCHAR(50)` | `NOT NULL` | |
| `color_name_ar` | `VARCHAR(50)` | `NOT NULL` | |
| `color_hex` | `CHAR(7)` | nullable | Swatch UI |
| `price` | `NUMERIC(10,2)` | `NOT NULL` | AED |
| `compare_at_price` | `NUMERIC(10,2)` | nullable | Strike-through original price |
| `weight_grams` | `INTEGER` | nullable | For shipping calculation |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | Per-variant purchasability — decision 17 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (product_id, size, color_name_en)`.

A variant is purchasable only when all three hold: `products.status = 'published'`, `product_variants.is_active = true`, and `inventory` shows available stock.

Relationships: belongs to one `product`; has one `inventory` row; optionally has `product_media`; referenced by `cart_items`, `order_items`, and `wishlist_items` (future).

### 5.6 `product_media`

Images and videos for a product, in one ordered gallery, optionally scoped to a specific variant.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `product_id` | `BIGINT` | FK → `products.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `product_variant_id` | `BIGINT` | FK → `product_variants.id`, `ON DELETE CASCADE`, nullable | Null = generic product-level media |
| `media_type` | `VARCHAR(10)` | `NOT NULL`, `CHECK (media_type IN ('image','video'))` | Images and videos share this table and one `sort_order` sequence |
| `url` | `VARCHAR(500)` | `NOT NULL` | Storage-provider-neutral URL (any CDN/object store) |
| `thumbnail_url` | `VARCHAR(500)` | nullable | Poster frame — expected for videos, optional for images |
| `alt_text_en` | `VARCHAR(255)` | nullable | Alt text for images; caption for videos |
| `alt_text_ar` | `VARCHAR(255)` | nullable | |
| `sort_order` | `INTEGER` | `NOT NULL`, default `0` | One ordering across both media types, so the storefront gallery lets a customer navigate images and videos as a single sequence |
| `is_primary` | `BOOLEAN` | `NOT NULL`, default `false` | Main/thumbnail item; app enforces at most one primary per product (and per variant, if scoped) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: belongs to one `product`, optionally scoped to one `product_variant`.

### 5.7 `inventory`

Stock tracking, one row per variant. See decision 6.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `product_variant_id` | `BIGINT` | FK → `product_variants.id`, `ON DELETE CASCADE`, `UNIQUE`, `NOT NULL` | 1:1 with variant |
| `quantity_on_hand` | `INTEGER` | `NOT NULL`, default `0`, `CHECK (quantity_on_hand >= 0)` | Physical stock |
| `quantity_reserved` | `INTEGER` | `NOT NULL`, default `0`, `CHECK (quantity_reserved >= 0)` | Held by open carts/pending orders |
| `low_stock_threshold` | `INTEGER` | `NOT NULL`, default `5` | Restock alert trigger |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Available-to-sell quantity (`quantity_on_hand - quantity_reserved`) is computed at the application level, not stored, to avoid drift.

Relationships: belongs to exactly one `product_variant`.

### 5.8 `shipping_methods`

Reusable shipping method definitions.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `code` | `VARCHAR(30)` | `UNIQUE`, `NOT NULL` | e.g. `standard`, `express`, `free` |
| `name_en` | `VARCHAR(100)` | `NOT NULL` | |
| `name_ar` | `VARCHAR(100)` | `NOT NULL` | |
| `description_en` | `TEXT` | nullable | |
| `description_ar` | `TEXT` | nullable | |
| `estimated_days_min` | `INTEGER` | `NOT NULL` | |
| `estimated_days_max` | `INTEGER` | `NOT NULL` | |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | Offered at checkout or not |
| `sort_order` | `INTEGER` | `NOT NULL`, default `0` | Checkout display order |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: has many `shipping_rates`; referenced by snapshot from `orders`.

### 5.9 `shipping_rates`

Price of a shipping method, per emirate, with an optional free-shipping threshold. See decision 19.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `shipping_method_id` | `BIGINT` | FK → `shipping_methods.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `emirate` | `VARCHAR(20)` | `NOT NULL`, `CHECK (emirate IN ('Abu Dhabi','Dubai','Sharjah','Ajman','Umm Al Quwain','Ras Al Khaimah','Fujairah'))` | Same set as `addresses.emirate` |
| `rate_amount` | `NUMERIC(10,2)` | `NOT NULL` | AED cost for this method in this emirate |
| `free_shipping_min_order_amount` | `NUMERIC(10,2)` | nullable | Waives the rate above this subtotal |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (shipping_method_id, emirate)`.

A dedicated free-shipping method can be modeled with `rate_amount = 0`, and/or any method can waive its rate above a threshold via `free_shipping_min_order_amount` — both patterns work without extra tables.

Relationships: belongs to one `shipping_method`.

### 5.10 `carts`

One active cart per guest session or per user. Ephemeral — hard-deleted after conversion to an order or expiry.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE CASCADE`, nullable | Null for guest carts |
| `guest_token` | `UUID` | nullable, `UNIQUE` | Stored client-side (cookie) for guest carts |
| `currency` | `CHAR(3)` | `NOT NULL`, default `'AED'` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `CHECK (user_id IS NOT NULL OR guest_token IS NOT NULL)`.

Relationships: has many `cart_items`.

### 5.11 `cart_items`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `cart_id` | `BIGINT` | FK → `carts.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `product_variant_id` | `BIGINT` | FK → `product_variants.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `quantity` | `INTEGER` | `NOT NULL`, `CHECK (quantity > 0)` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (cart_id, product_variant_id)` — re-adding a variant increments quantity instead of inserting a new row.

Cart items are not snapshotted: price and name are read live from the catalog until checkout.

Relationships: belongs to one `cart`; references one `product_variant`.

### 5.12 `coupons`

Discount codes, including the 10% first-order signup discount. See decision 10.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `code` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL` | |
| `discount_type` | `VARCHAR(10)` | `NOT NULL`, `CHECK (discount_type IN ('percentage','fixed'))` | |
| `discount_value` | `NUMERIC(10,2)` | `NOT NULL` | % (0–100) or fixed AED amount |
| `min_order_amount` | `NUMERIC(10,2)` | nullable | |
| `max_discount_amount` | `NUMERIC(10,2)` | nullable | Cap for percentage discounts |
| `usage_limit` | `INTEGER` | nullable | Total redemptions allowed; null = unlimited |
| `usage_count` | `INTEGER` | `NOT NULL`, default `0` | Global counter — insufficient alone for per-user enforcement (decision 10) |
| `requires_account` | `BOOLEAN` | `NOT NULL`, default `false` | Only registered users may redeem |
| `first_order_only` | `BOOLEAN` | `NOT NULL`, default `false` | Valid only if the user has no prior orders |
| `max_redemptions_per_user` | `INTEGER` | nullable, default `1` | Null = no per-user cap |
| `starts_at` | `TIMESTAMPTZ` | nullable | |
| `expires_at` | `TIMESTAMPTZ` | nullable | |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

The signup discount is a single seeded row (`code = 'WELCOME10'`, `discount_type = 'percentage'`, `discount_value = 10`, `requires_account = true`, `first_order_only = true`, `max_redemptions_per_user = 1`); no separate promotions table is needed. See `coupon_redemptions` (5.13) for reuse prevention.

Relationships: referenced by many `orders`; has many `coupon_redemptions`.

### 5.13 `coupon_redemptions`

Per-redemption audit and enforcement ledger — the mechanism that makes account- and first-order-restricted coupons actually enforceable. See decision 10.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `coupon_id` | `BIGINT` | FK → `coupons.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE CASCADE`, nullable | Null only for coupons that don't require an account |
| `order_id` | `BIGINT` | FK → `orders.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `email` | `VARCHAR(255)` | `NOT NULL` | Snapshotted at redemption time |
| `phone` | `VARCHAR(30)` | `NOT NULL` | Snapshotted at redemption time |
| `discount_amount` | `NUMERIC(10,2)` | `NOT NULL` | Snapshot of the amount actually granted |
| `redeemed_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (coupon_id, user_id) WHERE user_id IS NOT NULL` — prevents the same account redeeming a capped coupon twice. This covers the MVP's one per-user-capped coupon (cap of 1); a future cap greater than 1 would need an application-level count check instead (open question, section 8).

`email` and `phone` are indexed (not unique) so the application can flag redemption attempts that reuse contact details already tied to a different account.

Relationships: belongs to one `coupon`; optionally belongs to one `user`; belongs to one `order`.

### 5.14 `orders`

The checkout record. Supports both guest and registered-user orders.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `order_number` | `VARCHAR(30)` | `UNIQUE`, `NOT NULL` | Human-facing reference, e.g. `ORD-2026-000123` |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE SET NULL`, nullable | Null for guest orders |
| `guest_email` | `VARCHAR(255)` | nullable | Set for guest orders |
| `contact_email` | `VARCHAR(255)` | `NOT NULL` | Used for confirmations regardless of guest/user |
| `contact_phone` | `VARCHAR(30)` | `NOT NULL` | |
| `status` | `VARCHAR(20)` | `NOT NULL`, default `'pending'` | `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded` |
| `payment_status` | `VARCHAR(20)` | `NOT NULL`, default `'unpaid'` | `unpaid`, `paid`, `partially_refunded`, `refunded`, `failed` — denormalized summary of `payments` |
| `currency` | `CHAR(3)` | `NOT NULL`, default `'AED'` | |
| `subtotal` | `NUMERIC(10,2)` | `NOT NULL` | Before discount/shipping/tax |
| `discount_amount` | `NUMERIC(10,2)` | `NOT NULL`, default `0` | See decision 9 |
| `coupon_id` | `BIGINT` | FK → `coupons.id`, `ON DELETE SET NULL`, nullable | |
| `shipping_method_id` | `BIGINT` | FK → `shipping_methods.id`, `ON DELETE SET NULL`, nullable | See decision 11 |
| `shipping_method_name_en` | `VARCHAR(150)` | `NOT NULL` | Snapshotted at checkout |
| `shipping_method_name_ar` | `VARCHAR(150)` | `NOT NULL` | Snapshotted at checkout |
| `shipping_estimated_days_min` | `INTEGER` | nullable | Snapshotted at checkout |
| `shipping_estimated_days_max` | `INTEGER` | nullable | Snapshotted at checkout |
| `shipping_amount` | `NUMERIC(10,2)` | `NOT NULL`, default `0` | May be `0` if a free-shipping threshold was met |
| `tax_amount` | `NUMERIC(10,2)` | `NOT NULL`, default `0` | |
| `total_amount` | `NUMERIC(10,2)` | `NOT NULL` | `subtotal - discount_amount + shipping_amount + tax_amount` |
| `customer_note` | `TEXT` | nullable | |
| `placed_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `CHECK (user_id IS NOT NULL OR guest_email IS NOT NULL)`.

Relationships: optionally belongs to a `user`; optionally references a `coupon` and a `shipping_method`; has many `order_items`, `payments`, and at most one `coupon_redemptions` row; has two `order_addresses` (shipping and billing).

### 5.15 `order_addresses`

Snapshot of the shipping and billing address used for an order. See decision 8.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `order_id` | `BIGINT` | FK → `orders.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `address_id` | `BIGINT` | FK → `addresses.id`, `ON DELETE SET NULL`, nullable | Original address, if it still exists |
| `address_type` | `VARCHAR(10)` | `NOT NULL`, `CHECK (address_type IN ('shipping','billing'))` | |
| `full_name` | `VARCHAR(200)` | `NOT NULL` | Snapshotted |
| `phone` | `VARCHAR(30)` | `NOT NULL` | Snapshotted |
| `emirate` | `VARCHAR(20)` | `NOT NULL`, `CHECK (emirate IN ('Abu Dhabi','Dubai','Sharjah','Ajman','Umm Al Quwain','Ras Al Khaimah','Fujairah'))` | Snapshotted |
| `city` | `VARCHAR(100)` | nullable | Snapshotted |
| `area` | `VARCHAR(100)` | `NOT NULL` | Snapshotted |
| `street` | `VARCHAR(255)` | `NOT NULL` | Snapshotted |
| `building` | `VARCHAR(100)` | `NOT NULL` | Snapshotted |
| `apartment_or_villa_no` | `VARCHAR(50)` | nullable | Snapshotted |
| `landmark` | `VARCHAR(255)` | nullable | Snapshotted |
| `postal_code` | `VARCHAR(20)` | nullable | Snapshotted |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (order_id, address_type)`.

Relationships: belongs to one `order`; optionally references the original `address`.

### 5.16 `order_items`

Order line items, fully snapshotted. See decision 4.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `order_id` | `BIGINT` | FK → `orders.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `product_variant_id` | `BIGINT` | FK → `product_variants.id`, `ON DELETE SET NULL`, nullable | Soft reference — decision 5 |
| `sku` | `VARCHAR(64)` | `NOT NULL` | Snapshotted |
| `product_name_en` | `VARCHAR(255)` | `NOT NULL` | Snapshotted |
| `product_name_ar` | `VARCHAR(255)` | `NOT NULL` | Snapshotted |
| `variant_attributes` | `VARCHAR(255)` | `NOT NULL` | e.g. `"Size: M, Color: Red"` |
| `unit_price` | `NUMERIC(10,2)` | `NOT NULL` | Snapshotted, AED |
| `quantity` | `INTEGER` | `NOT NULL`, `CHECK (quantity > 0)` | |
| `line_total` | `NUMERIC(10,2)` | `NOT NULL` | `unit_price * quantity` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: belongs to one `order`; optionally references a `product_variant`.

### 5.17 `payments`

Payment attempts against an order, provider-neutral. See decision 12.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `order_id` | `BIGINT` | FK → `orders.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `provider` | `VARCHAR(30)` | `NOT NULL` | e.g. `network_international`, `telr`, `paytabs`, `apple_pay`, `google_pay`, `tabby`, `tamara`, `manual` (cash on delivery) |
| `provider_reference` | `VARCHAR(255)` | nullable | Gateway transaction/charge ID |
| `method` | `VARCHAR(30)` | `NOT NULL`, `CHECK (method IN ('card','apple_pay','google_pay','cash_on_delivery','tabby','tamara'))` | Customer-facing payment choice |
| `status` | `VARCHAR(20)` | `NOT NULL`, default `'pending'` | `pending`, `authorized`, `captured`, `failed`, `refunded` |
| `amount` | `NUMERIC(10,2)` | `NOT NULL` | AED |
| `currency` | `CHAR(3)` | `NOT NULL`, default `'AED'` | |
| `failure_reason` | `VARCHAR(255)` | nullable | |
| `paid_at` | `TIMESTAMPTZ` | nullable | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Tabby and Tamara can appear as both `method` and `provider`, since each acts as its own processor for buy-now-pay-later. Enabling either later is an application change; a dedicated installment/plan-reference column can be added at that point if required (open question, section 8).

Relationships: belongs to one `order`.

### 5.18 `wishlists`

Future scope — not part of the MVP. See decision 13.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `user_id` | `BIGINT` | FK → `users.id`, `ON DELETE CASCADE`, `UNIQUE`, `NOT NULL` | 1:1 with user |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Relationships: belongs to one `user`; has many `wishlist_items`.

### 5.19 `wishlist_items`

Future scope — not part of the MVP.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `wishlist_id` | `BIGINT` | FK → `wishlists.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `product_variant_id` | `BIGINT` | FK → `product_variants.id`, `ON DELETE CASCADE`, `NOT NULL` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

Constraint: `UNIQUE (wishlist_id, product_variant_id)`.

Relationships: belongs to one `wishlist`; references one `product_variant`.

### 5.20 `homepage_sections`

Admin-manageable, reorderable homepage content blocks. Standalone — no foreign keys in or out. See decision 20.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `section_type` | `VARCHAR(30)` | `NOT NULL`, `CHECK (section_type IN ('hero','collections','featured_products','offers','banner','brand_story','custom_block'))` | |
| `title_en` | `VARCHAR(255)` | nullable | |
| `title_ar` | `VARCHAR(255)` | nullable | |
| `content_en` | `TEXT` | nullable | Mainly used by `brand_story` and `custom_block` |
| `content_ar` | `TEXT` | nullable | |
| `media_url` | `VARCHAR(500)` | nullable | Storage-provider-neutral URL |
| `media_type` | `VARCHAR(10)` | nullable, `CHECK (media_type IN ('image','video'))` | |
| `config` | `JSONB` | `NOT NULL`, default `'{}'` | Section-specific settings, see below |
| `display_order` | `INTEGER` | `NOT NULL`, default `0` | Admin-editable homepage ordering |
| `is_active` | `BOOLEAN` | `NOT NULL`, default `true` | |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, default `now()` | |

`config` holds only what varies by `section_type`, keeping the typed columns shared across all types. Examples (Arabic values shown as placeholders):

- `hero`: `{"cta_text_en": "Shop Now", "cta_text_ar": "<Arabic translation>", "cta_url": "/collections/new-in"}`
- `collections`: `{"category_ids": [12, 15, 20]}`
- `featured_products`: `{"product_ids": [101, 142, 178], "limit": 8}`
- `offers`: `{"banner_text_en": "20% off summer styles", "banner_text_ar": "<Arabic translation>", "coupon_code": "SUMMER20"}`
- `banner`: `{"link_url": "/sale", "background_color": "#111111"}`
- `brand_story`: `{}` — uses `content_en`/`content_ar` directly
- `custom_block`: arbitrary JSON, shape owned by the admin/frontend contract

IDs referenced inside `config` (e.g. `category_ids`, `product_ids`) are not foreign-key enforced — a referenced product or category could later be deleted without `config` being updated. This is a deliberate flexibility trade-off, tracked in section 8.

Relationships: none.

## 6. Relationship explanations

- **Users, addresses, and orders:** a user stores reusable, emirate-based addresses; at checkout, the order takes a snapshot (`order_addresses`) rather than a live pointer, so editing or deleting a saved address never rewrites a past order. Guests skip the reusable step and go straight into the snapshot with `address_id` null.

- **Categories and products:** the self-referencing `categories` table models a two-level hierarchy with one table instead of two, with the level cap enforced by the application (decision 14). Each product belongs to exactly one category; multi-category tagging is a future join table, not a breaking change.

- **Products, variants, and inventory:** a product is the single browsing/marketing entity — one detail page, one media gallery, one description, one SEO record, one lifecycle `status`. Its variants are what customers actually add to cart, each with its own SKU, price, availability flag, and stock row.

- **Products and product media:** one gallery table holds both images and videos per product (optionally narrowed to a variant), ordered by a shared `sort_order` so browsing feels like one continuous gallery rather than separate image and video sections.

- **Carts, cart items, and variants:** carts hold line items that reference live variants with no snapshotting, since a cart reflects current catalog state — including price changes — right up until checkout.

- **Shipping methods, rates, and orders:** a method has one rate per emirate, optionally waived above a subtotal threshold; the resolved method and rate are snapshotted onto the order at checkout so later rate or method changes never alter a historical order's shipping details.

- **Orders, order items, order addresses, and payments:** placing an order freezes its data — line items, addresses, and the chosen shipping method are all snapshotted, and the order's totals are stored values, not computed on read, so an order remains accurate independent of later catalog, address, or shipping changes.

- **Coupons, coupon redemptions, and orders:** a coupon is a reusable, optionally account-restricted rule; `coupon_redemptions` is the audit/enforcement trail of who used it, keyed by user and by snapshotted contact details so abuse is detectable even across different accounts. The order itself only stores the resulting discount and a nullable pointer back to the coupon.

- **Wishlists, wishlist items, and variants (future scope):** modeled at the variant level, consistent with carts and orders, so a saved item captures the exact size/color — included for forward compatibility only, with no functionality shipping yet.

- **Homepage sections:** a standalone, admin-managed table with no foreign keys, composing the storefront homepage by type and order, using `config` JSONB for whatever is section-specific.

- **Bilingual fields:** everywhere customer-facing text appears — categories, products, variant color names, product media captions, shipping method names, order-item snapshots, homepage section titles/content — `_en` and `_ar` sit side by side so either locale can be served without a join, and snapshots stay bilingual even after the source record changes.

## 7. Indexing notes

For the future implementation ticket, not part of the ERD itself:

- B-tree indexes on all foreign-key columns (Postgres does not auto-index them).
- Unique indexes on `products.slug` and `categories.slug` for storefront routing.
- Composite index on `product_variants (product_id, is_active)` for catalog listing queries.
- Composite index on `products (status, category_id)` for category listings filtered to `published`.
- Index on `product_media (product_id, sort_order)` for gallery ordering.
- Index on `orders (user_id, created_at DESC)` for order-history pages.
- Index on `orders.status` for admin/order-management filtering.
- Partial unique index on `carts (guest_token) WHERE guest_token IS NOT NULL`.
- Unique index on `shipping_rates (shipping_method_id, emirate)` — already a table constraint, noted for emphasis.
- Partial unique index on `coupon_redemptions (coupon_id, user_id) WHERE user_id IS NOT NULL`, plus non-unique indexes on `coupon_redemptions (email)` and `coupon_redemptions (phone)` for abuse checks.
- Composite index on `homepage_sections (is_active, display_order)` for the homepage render query.
- Optional GIN index on `homepage_sections.config` if it ever needs to be queried by content rather than read whole.

## 8. Open questions

- Multi-warehouse inventory — currently one `inventory` row per variant, implicitly single-location.
- Multi-category tagging per product — currently one category per product.
- VAT/tax rules beyond a flat `tax_amount` on the order — no rate table yet; needed if UAE VAT treatment becomes category-specific.
- Itemized/partial refunds — `payments.status` currently only tracks `refunded` as a whole.
- `homepage_sections.config` references category/product IDs without FK enforcement, so a referenced record could be deleted without `config` being updated; needs app-layer validation, a periodic integrity check, or real join tables later if this becomes recurring.
- `coupons.max_redemptions_per_user` greater than 1 is not enforceable by the current unique constraint on `coupon_redemptions`, which only supports a cap of exactly 1; a count-based check would be needed for a higher per-user cap.
- Tabby/Tamara will likely need provider-specific fields (installment plan ID, merchant reference) once actually integrated; today's generic `provider`/`provider_reference` columns are a placeholder, not a final contract.
- Two-level category depth is enforced only by application logic, not a database constraint; a trigger could enforce it later if that gap ever causes a real data-integrity issue.

## 9. Entity summary

20 entities: `users`, `addresses`, `categories`, `products`, `product_variants`, `product_media`, `inventory`, `shipping_methods`, `shipping_rates`, `carts`, `cart_items`, `coupons`, `coupon_redemptions`, `orders`, `order_addresses`, `order_items`, `payments`, `wishlists` (future scope), `wishlist_items` (future scope), `homepage_sections`.
