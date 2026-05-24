CREATE TABLE IF NOT EXISTS raw.oraimo_products (
    scrape_run_id TEXT NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL,
    source_system TEXT NOT NULL DEFAULT 'ORAIMO',
    source_product_key TEXT NOT NULL,
    category TEXT,
    product_url TEXT,
    title TEXT,
    short_description TEXT,
    price_now_raw TEXT,
    price_now_num NUMERIC,
    price_was_raw TEXT,
    price_was_num NUMERIC,
    currency TEXT,
    main_image_url TEXT,
    ean TEXT,
    model TEXT,
    stock_status TEXT,
    slug TEXT,
    raw_payload JSONB,
    record_loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_oraimo_products_key
ON raw.oraimo_products (source_product_key, scraped_at DESC);

CREATE TABLE IF NOT EXISTS raw.kilimall_inventory (
    import_run_id TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL,
    store_name TEXT NOT NULL,
    marketplace TEXT NOT NULL DEFAULT 'KILIMALL',
    listing_id TEXT,
    sku_id TEXT,
    vendor_product_id TEXT,
    title TEXT,
    kilimall_url TEXT,
    selling_price NUMERIC,
    fbk_inventory NUMERIC,
    non_fbk_inventory NUMERIC,
    status TEXT,
    raw_payload JSONB,
    record_loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kilimall_inventory_sku
ON raw.kilimall_inventory (store_name, sku_id, imported_at DESC);

CREATE TABLE IF NOT EXISTS raw.kilimall_completed_orders (
    import_run_id TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL,
    store_name TEXT NOT NULL,
    order_number TEXT,
    order_id TEXT,
    sku_id TEXT,
    sku_title TEXT,
    sold_qty INTEGER,
    deal_price NUMERIC,
    promotion_type TEXT,
    discount NUMERIC,
    order_time TIMESTAMPTZ,
    payment_time TIMESTAMPTZ,
    complete_time TIMESTAMPTZ,
    status TEXT,
    raw_payload JSONB,
    record_loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kilimall_completed_orders
ON raw.kilimall_completed_orders (store_name, order_number, sku_id);

CREATE TABLE IF NOT EXISTS raw.kilimall_weekly_statement_lines (
    import_run_id TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL,
    source_filename TEXT,
    sheet_name TEXT,
    statement_start_date DATE,
    statement_end_date DATE,
    store_id TEXT,
    store_name TEXT,
    order_sn TEXT,
    payment_time TIMESTAMPTZ,
    finished_time TIMESTAMPTZ,
    goods_id TEXT,
    goods_name TEXT,
    goods_price NUMERIC,
    goods_num INTEGER,
    complete_amount NUMERIC,
    commission NUMERIC,
    ds_quality_inspection_fee NUMERIC,
    fine NUMERIC,
    warehouse_operation_fee NUMERIC,
    warehouse_storage_fee NUMERIC,
    ds_processing_fee NUMERIC,
    lite_shipping_fee NUMERIC,
    customer_service_discount_fee NUMERIC,
    other_deductions NUMERIC,
    billing_appeal NUMERIC,
    compensations NUMERIC,
    settlement_payable NUMERIC,
    raw_payload JSONB,
    record_loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kilimall_weekly_statement_order
ON raw.kilimall_weekly_statement_lines (store_name, order_sn);
