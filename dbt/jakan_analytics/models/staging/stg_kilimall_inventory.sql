select
    import_run_id, imported_at, store_name, marketplace, listing_id, sku_id,
    vendor_product_id, title as kilimall_title, kilimall_url, selling_price,
    fbk_inventory, non_fbk_inventory, status as listing_status,
    case
        when lower(coalesce(status, '')) in ('active', 'online', 'selling', 'on sale') then true
        when lower(coalesce(status, '')) in ('inactive', 'offline', 'delisted', 'not active') then false
        else null
    end as is_listing_active
from {{ source('raw', 'kilimall_inventory') }}
where coalesce(sku_id, '') <> ''
