select
    scrape_run_id, scraped_at, source_system, source_product_key, category,
    product_url, title as supplier_title, short_description,
    price_now_raw, price_now_num, price_was_raw, price_was_num, currency,
    main_image_url, ean, model, stock_status, slug,
    case
        when lower(stock_status) in ('instock', 'in_stock', 'available') then true
        when lower(stock_status) in ('outofstock', 'out_of_stock', 'out of stock') then false
        else null
    end as is_in_stock
from {{ source('raw', 'oraimo_products') }}
