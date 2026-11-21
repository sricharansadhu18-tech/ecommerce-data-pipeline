with first_last as (
    select
        customer_unique_id,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        count(distinct order_id) as lifetime_orders,
        sum(payment_total) as lifetime_payment_total
    from {{ ref('int_orders_enriched') }}
    group by customer_unique_id
),

latest_location as (
    select
        customer_unique_id,
        customer_city,
        customer_state
    from (
        select
            customer_unique_id,
            customer_city,
            customer_state,
            row_number() over (
                partition by customer_unique_id
                order by order_date desc, order_id desc
            ) as rn
        from {{ ref('int_orders_enriched') }}
    ) ranked
    where rn = 1
)

select
    md5(fl.customer_unique_id) as customer_key,
    fl.customer_unique_id,
    loc.customer_city,
    loc.customer_state,
    fl.first_order_date,
    fl.last_order_date,
    fl.lifetime_orders,
    fl.lifetime_payment_total,
    (fl.lifetime_orders >= 2) as is_repeat_customer
from first_last fl
inner join latest_location loc
    on fl.customer_unique_id = loc.customer_unique_id
