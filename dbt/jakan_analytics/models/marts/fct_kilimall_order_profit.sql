with orders as (
    select * from {{ ref('stg_kilimall_completed_orders') }}
),
finance as (
    select
        store_name, order_sn, goods_id,
        sum(coalesce(commission, 0)) as commission,
        sum(coalesce(ds_quality_inspection_fee, 0)) as ds_quality_inspection_fee,
        sum(coalesce(fine, 0)) as fine,
        sum(coalesce(warehouse_operation_fee, 0)) as warehouse_operation_fee,
        sum(coalesce(warehouse_storage_fee, 0)) as warehouse_storage_fee,
        sum(coalesce(ds_processing_fee, 0)) as ds_processing_fee,
        sum(coalesce(lite_shipping_fee, 0)) as lite_shipping_fee,
        sum(coalesce(customer_service_discount_fee, 0)) as customer_service_discount_fee,
        sum(coalesce(other_deductions, 0)) as other_deductions,
        sum(coalesce(billing_appeal, 0)) as billing_appeal,
        sum(coalesce(compensations, 0)) as compensations,
        sum(coalesce(settlement_payable, 0)) as settlement_payable
    from {{ ref('stg_kilimall_finance_lines') }}
    group by 1,2,3
),
joined as (
    select
        o.store_name, o.order_number, o.order_id, o.sku_id, o.sku_title,
        o.sold_qty, o.deal_price, o.discount, o.status,
        o.order_time, o.payment_time, o.complete_time,
        lm.internal_sku_id,
        sc.price_now_num as supplier_buy_price,
        sc.total_cost_basis as estimated_unit_cost,
        coalesce(o.sold_qty, 0) * coalesce(sc.total_cost_basis, 0) as estimated_total_cost,
        coalesce(o.sold_qty, 0) * coalesce(o.deal_price, 0) as gross_sales_amount,
        f.*
    from orders o
    left join {{ ref('sku_listing_map') }} lm on lm.sku_id = o.sku_id and lm.active = true
    left join {{ ref('sku_source_map') }} sm on sm.internal_sku_id = lm.internal_sku_id and sm.active = true
    left join {{ ref('int_price_calculation') }} sc on sc.source_product_key = sm.source_product_key
    left join finance f on f.order_sn = o.order_number and (f.goods_id = o.sku_id or f.goods_id is null)
)
select
    *,
    coalesce(commission, 0) + coalesce(ds_quality_inspection_fee, 0) + coalesce(fine, 0)
    + coalesce(warehouse_operation_fee, 0) + coalesce(warehouse_storage_fee, 0)
    + coalesce(ds_processing_fee, 0) + coalesce(lite_shipping_fee, 0)
    + coalesce(customer_service_discount_fee, 0) + coalesce(other_deductions, 0)
    - coalesce(billing_appeal, 0) - coalesce(compensations, 0) as total_platform_fees,
    gross_sales_amount - coalesce(discount, 0) - estimated_total_cost
    - (
        coalesce(commission, 0) + coalesce(ds_quality_inspection_fee, 0) + coalesce(fine, 0)
        + coalesce(warehouse_operation_fee, 0) + coalesce(warehouse_storage_fee, 0)
        + coalesce(ds_processing_fee, 0) + coalesce(lite_shipping_fee, 0)
        + coalesce(customer_service_discount_fee, 0) + coalesce(other_deductions, 0)
        - coalesce(billing_appeal, 0) - coalesce(compensations, 0)
    ) as estimated_net_profit
from joined
