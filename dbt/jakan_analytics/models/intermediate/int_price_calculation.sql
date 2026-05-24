with supplier as (
    select * from {{ ref('int_latest_oraimo_products') }}
),
rules as (
    select * from {{ ref('price_rules') }} where active = true
),
joined as (
    select
        s.*,
        coalesce(r.cost_buffer, d.cost_buffer, 250) as cost_buffer,
        coalesce(r.target_margin_pct, d.target_margin_pct, 0.30) as target_margin_pct,
        coalesce(r.rounding_step, d.rounding_step, 50) as rounding_step,
        coalesce(r.min_profit, d.min_profit, 300) as min_profit
    from supplier s
    left join rules r on r.business_unit_id = 'BU_PHONE' and lower(r.category) = lower(s.category)
    left join rules d on d.business_unit_id = 'BU_PHONE' and d.category = 'DEFAULT'
),
calc as (
    select
        *,
        coalesce(price_now_num, 0) + cost_buffer as total_cost_basis,
        greatest(
            (coalesce(price_now_num, 0) + cost_buffer) / nullif((1 - target_margin_pct), 0),
            (coalesce(price_now_num, 0) + cost_buffer) + min_profit
        ) as raw_proposed_sp
    from joined
)
select
    *,
    ceiling(raw_proposed_sp / nullif(rounding_step, 0)) * rounding_step as proposed_selling_price,
    (ceiling(raw_proposed_sp / nullif(rounding_step, 0)) * rounding_step) - total_cost_basis as projected_profit
from calc
