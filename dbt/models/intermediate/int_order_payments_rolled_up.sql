select
    order_id,
    sum(payment_value) as payment_total,
    count(*) as payment_count,
    max(payment_installments) as max_installments,
    -- primary payment type by value
    (array_agg(payment_type order by payment_value desc))[1] as primary_payment_type
from {{ ref('stg_order_payments') }}
group by order_id
