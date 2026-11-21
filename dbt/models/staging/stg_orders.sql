select
    order_id,
    customer_id,
    lower(btrim(order_status)) as order_status,
    order_purchase_timestamp::timestamp as order_purchase_timestamp,
    order_approved_at::timestamp as order_approved_at,
    order_delivered_carrier_date::timestamp as order_delivered_carrier_date,
    order_delivered_customer_date::timestamp as order_delivered_customer_date,
    order_estimated_delivery_date::timestamp as order_estimated_delivery_date,
    order_purchase_timestamp::date as order_date,
    order_delivered_customer_date::date as delivered_date,
    order_estimated_delivery_date::date as estimated_delivery_date
from {{ source('raw', 'orders') }}
