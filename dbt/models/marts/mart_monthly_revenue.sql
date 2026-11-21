select
    d.year_month,
    d.year,
    d.month,
    trim(d.month_name) as month_name,
    count(*) as orders,
    count(*) filter (where o.is_delivered) as delivered_orders,
    sum(o.payment_total) as payment_total,
    sum(o.item_price_total) as merchandise_revenue,
    round(
        (sum(o.payment_total) / nullif(count(*), 0))::numeric,
        2
    ) as aov
from {{ ref('fct_orders') }} o
inner join {{ ref('dim_date') }} d
    on o.order_date_key = d.date_key
group by 1, 2, 3, 4
