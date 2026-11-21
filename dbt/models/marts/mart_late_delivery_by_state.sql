select
    customer_state,
    count(*) as delivered_orders,
    count(*) filter (where is_late) as late_orders,
    round((100.0 * avg(is_late::int))::numeric, 1) as late_rate_pct,
    round(avg(delivery_days)::numeric, 2) as avg_delivery_days,
    round(avg(review_score)::numeric, 2) as avg_review_score
from {{ ref('fct_orders') }}
where is_delivered
  and is_late is not null
group by 1
