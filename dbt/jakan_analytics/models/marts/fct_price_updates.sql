with base as (
    select
        s.*, lm.sku_id, lm.listing_id, k.store_name, k.kilimall_title,
        k.kilimall_url, k.selling_price as current_kilimall_sp,
        k.listing_status, k.is_listing_active
    from {{ ref('int_price_calculation') }} s
    join {{ ref('sku_source_map') }} sm
        on sm.source_product_key = s.source_product_key and sm.source_system = 'ORAIMO' and sm.active = true
    join {{ ref('sku_listing_map') }} lm
        on lm.internal_sku_id = sm.internal_sku_id and lm.marketplace = 'KILIMALL' and lm.active = true
    left join {{ ref('int_latest_kilimall_inventory') }} k on k.sku_id = lm.sku_id
)
select
    *,
    proposed_selling_price - current_kilimall_sp as price_diff,
    true as needs_price_update
from base
where is_in_stock = true
  and coalesce(is_listing_active, true) = true
  and (current_kilimall_sp is null or abs(proposed_selling_price - current_kilimall_sp) >= 50)
