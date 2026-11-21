select
    order_id,
    count(*) as item_count,
    count(distinct product_id) as distinct_product_count,
    count(distinct seller_id) as distinct_seller_count,
    sum(price) as item_price_total,
    sum(freight_value) as freight_total,
    sum(price + freight_value) as item_plus_freight_total
from {{ ref('stg_order_items') }}
group by order_id
