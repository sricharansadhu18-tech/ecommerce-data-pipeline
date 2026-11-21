select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.order_date,
    o.delivered_date,
    o.estimated_delivery_date,
    coalesce(i.item_count, 0) as item_count,
    coalesce(i.item_price_total, 0) as item_price_total,
    coalesce(i.freight_total, 0) as freight_total,
    coalesce(p.payment_total, 0) as payment_total,
    p.primary_payment_type,
    r.review_score,
    r.avg_review_score,
    case
        when o.delivered_date is not null and o.order_date is not null
            then o.delivered_date - o.order_date
    end as delivery_days,
    case
        when o.estimated_delivery_date is not null and o.order_date is not null
            then o.estimated_delivery_date - o.order_date
    end as estimated_delivery_days,
    case
        when o.delivered_date is not null and o.estimated_delivery_date is not null
            then o.delivered_date > o.estimated_delivery_date
    end as is_late,
    (o.order_status = 'delivered') as is_delivered
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
    on o.customer_id = c.customer_id
left join {{ ref('int_order_items_rolled_up') }} i
    on o.order_id = i.order_id
left join {{ ref('int_order_payments_rolled_up') }} p
    on o.order_id = p.order_id
left join {{ ref('int_order_reviews_rolled_up') }} r
    on o.order_id = r.order_id
