select order_id, order_item_id, price
from {{ ref('fct_order_items') }}
where price < 0 or freight_value < 0
