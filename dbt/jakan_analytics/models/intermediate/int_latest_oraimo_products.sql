with ranked as (
    select *, row_number() over (partition by source_product_key order by scraped_at desc) as rn
    from {{ ref('stg_oraimo_products') }}
)
select * from ranked where rn = 1
