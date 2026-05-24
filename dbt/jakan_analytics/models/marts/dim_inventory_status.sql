select
    source_product_key, supplier_title, category, product_url as supplier_url,
    stock_status, is_in_stock, price_now_num as supplier_buy_price,
    total_cost_basis, proposed_selling_price, projected_profit
from {{ ref('int_price_calculation') }}
