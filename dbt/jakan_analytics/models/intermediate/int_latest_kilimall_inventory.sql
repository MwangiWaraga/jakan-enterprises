with ranked as (
    select *, row_number() over (partition by store_name, sku_id order by imported_at desc) as rn
    from {{ ref('stg_kilimall_inventory') }}
)
select * from ranked where rn = 1
