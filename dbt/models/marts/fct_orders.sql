select
    o.order_id,
    c.customer_key,
    o.customer_unique_id,
    od.date_key as order_date_key,
    dd.date_key as delivered_date_key,
    ed.date_key as estimated_delivery_date_key,
    o.order_date,
    o.delivered_date,
    o.estimated_delivery_date,
    o.order_status,
    o.is_delivered,
    o.is_late,
    o.delivery_days,
    o.estimated_delivery_days,
    o.item_count,
    o.item_price_total,
    o.freight_total,
    o.payment_total,
    o.primary_payment_type,
    o.review_score,
    o.avg_review_score,
    o.customer_city,
    o.customer_state
from {{ ref('int_orders_enriched') }} o
left join {{ ref('dim_customers') }} c
    on o.customer_unique_id = c.customer_unique_id
left join {{ ref('dim_date') }} od
    on o.order_date = od.date_day
left join {{ ref('dim_date') }} dd
    on o.delivered_date = dd.date_day
left join {{ ref('dim_date') }} ed
    on o.estimated_delivery_date = ed.date_day
