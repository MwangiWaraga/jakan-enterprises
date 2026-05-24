select *
from {{ source('raw', 'kilimall_completed_orders') }}
where coalesce(order_number, order_id) is not null
