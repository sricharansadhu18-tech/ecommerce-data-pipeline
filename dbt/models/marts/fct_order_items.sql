select
    i.order_id,
    i.order_item_id,
    p.product_key,
    i.product_id,
    s.seller_key,
    i.seller_id,
    c.customer_key,
    od.date_key as order_date_key,
    o.order_date,
    o.order_status,
    i.price,
    i.freight_value,
    (i.price + i.freight_value) as line_total,
    o.customer_state,
    pr.product_category_name_english
from {{ ref('stg_order_items') }} i
inner join {{ ref('int_orders_enriched') }} o
    on i.order_id = o.order_id
left join {{ ref('dim_products') }} p
    on i.product_id = p.product_id
left join {{ ref('dim_sellers') }} s
    on i.seller_id = s.seller_id
left join {{ ref('dim_customers') }} c
    on o.customer_unique_id = c.customer_unique_id
left join {{ ref('dim_date') }} od
    on o.order_date = od.date_day
left join {{ ref('stg_products') }} pr
    on i.product_id = pr.product_id
