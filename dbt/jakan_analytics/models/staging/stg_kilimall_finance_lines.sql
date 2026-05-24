select
    *,
    coalesce(commission, 0) as commission_clean,
    coalesce(fine, 0) as fine_clean,
    coalesce(ds_processing_fee, 0) as ds_processing_fee_clean,
    coalesce(lite_shipping_fee, 0) as lite_shipping_fee_clean
from {{ source('raw', 'kilimall_weekly_statement_lines') }}
