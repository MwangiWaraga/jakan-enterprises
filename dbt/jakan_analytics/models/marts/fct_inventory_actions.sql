with supplier as (
    select * from {{ ref('int_price_calculation') }}
),
source_map as (
    select * from {{ ref('sku_source_map') }} where active = true
),
listing_map as (
    select * from {{ ref('sku_listing_map') }} where active = true
),
kil as (
    select * from {{ ref('int_latest_kilimall_inventory') }}
),
mapped as (
    select
        s.source_product_key, s.supplier_title, s.category, s.product_url as supplier_url,
        s.stock_status, s.is_in_stock, s.price_now_num as supplier_buy_price,
        s.total_cost_basis, s.proposed_selling_price, s.projected_profit,
        sm.internal_sku_id, lm.store_id, lm.marketplace, lm.listing_id, lm.sku_id,
        k.store_name, k.kilimall_title, k.kilimall_url,
        k.selling_price as current_kilimall_sp, k.listing_status, k.is_listing_active
    from supplier s
    left join source_map sm on sm.source_system = 'ORAIMO' and sm.source_product_key = s.source_product_key
    left join listing_map lm on lm.internal_sku_id = sm.internal_sku_id and lm.marketplace = 'KILIMALL'
    left join kil k on k.sku_id = lm.sku_id
)
select 'OSS_DELIST' as action_type, 'Supplier out of stock but Kilimall appears active' as action_reason, *
from mapped
where is_in_stock = false and coalesce(is_listing_active, true) = true and sku_id is not null
union all
select 'RESTOCK_REACTIVATE' as action_type, 'Supplier is back in stock but Kilimall listing appears inactive' as action_reason, *
from mapped
where is_in_stock = true and is_listing_active = false and sku_id is not null
union all
select 'NOT_POSTED' as action_type, 'Supplier product is in stock but has no Kilimall SKU mapping/listing yet' as action_reason, *
from mapped
where is_in_stock = true and sku_id is null
