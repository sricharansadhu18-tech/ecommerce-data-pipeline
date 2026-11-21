select
    order_id,
    payment_sequential,
    lower(btrim(payment_type)) as payment_type,
    payment_installments,
    payment_value
from {{ source('raw', 'order_payments') }}
