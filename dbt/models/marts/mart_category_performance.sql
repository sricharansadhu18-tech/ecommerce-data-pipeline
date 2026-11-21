select
    product_category_name_english as category,
    count(*) as line_items,
    count(distinct order_id) as orders,
    sum(price) as merchandise_revenue,
    sum(freight_value) as freight_total,
    round((sum(price) / nullif(count(distinct order_id), 0))::numeric, 2) as revenue_per_order
from {{ ref('fct_order_items') }}
group by 1
