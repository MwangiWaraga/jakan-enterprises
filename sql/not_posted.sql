-- finds products in stock at oraimo but not on kilimall (price <= 15000)
-- calculates proposed selling price and projected profit based on your rules.

with config as (
  -- static business rules and fees
  select
    100::numeric as ds_fee,
    150::numeric as errand_fee,
    350::numeric as profit_floor,
    0.15::numeric as default_commission_rate,
    0.06::numeric as phone_commission_rate
),

oraimo_latest as (
  -- most recent record for each oraimo product
  select
    source_product_key,
    scraped_at,
    product_url,
    category,
    title,
    price_now_num,
    stock_status,
    row_number() over (
      partition by source_product_key
      order by scraped_at desc
    ) as rn
  from raw.oraimo_products
),

oraimo_raw as (
  -- latest oraimo products with shortened title for matching
  select
    scraped_at                                                                                     as web_scrap_ts,
    product_url                                                                                    as oraimo_url,
    'Oraimo'                                                                                       as brand,
    category,
    initcap(title)                                                                                 as oraimo_title,
    lower(left(trim(title), 18))                                                                    as oraimo_shortened_title,
    price_now_num                                                                                  as current_price,
    source_product_key                                                                             as product_id,
    stock_status
  from oraimo_latest
  where rn = 1
    and title is not null
)

-- select stock_status from oraimo_raw group by 1


, kilimall_raw as (
  -- distinct list of shortened titles from active kilimall listings
  select 
    listing_id,
	sku_id,
    title                                                                                         as kilimall_title,
    lower(left(trim(substring(title, length(split_part(title, ' ', 1)) + 2)), 18))                as kil_shortened_title,
	concat('https://www.kilimall.co.ke/listing/', listing_id)                                     as kilimall_url,
	selling_price                                                                                 as kilimall_sp,
	status,
	-- record_loaded_at,
    row_number() over (
      partition by sku_id
      order by record_loaded_at desc
    ) as rn	
  from raw.kilimall_inventory
  where 
    lower(title) like '%oraimo%'
	-- and  listing_id = '1001751846'
)

-- goal is to activate inactive items that oraimo have restocked
-- remove/deactive out of stock items already posted on kilimall  
-- never posted 
-- select status from kilimall_raw group by 1

, out_of_stock as (
   select 
     k.listing_id,
     k.sku_id,
     k.kilimall_title,
     o.oraimo_title,
     k.kilimall_url,
     o.oraimo_url,
     k.status,
     o.oraimo_shortened_title, k.kil_shortened_title
   from kilimall_raw k
   join oraimo_raw o  
     on o.oraimo_shortened_title = k.kil_shortened_title
   where
     o.stock_status = 'OutOfStock'
     and k.status = 'ACTIVE'
	 and k.rn = 1
)


, not_active as (
   select 
     k.listing_id,
     k.sku_id,
     k.kilimall_title,
     o.oraimo_title,
     k.kilimall_url,
     o.oraimo_url,
     k.status,
     o.oraimo_shortened_title, k.kil_shortened_title
   from kilimall_raw k
   join oraimo_raw o  
     on o.oraimo_shortened_title = k.kil_shortened_title
   where
     o.stock_status = 'InStock'
     and k.status ilike '%inactive%'
	 and k.rn = 1
)


select *, 'Not Active' as action_type from not_active

union all

select *,  'OOS' as action_type  from out_of_stock 

