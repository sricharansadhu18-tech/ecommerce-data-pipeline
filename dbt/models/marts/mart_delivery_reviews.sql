select
    review_score,
    count(*) as delivered_orders,
    round(avg(delivery_days)::numeric, 2) as avg_delivery_days,
    round(
        (100.0 * avg(is_late::int) filter (where is_late is not null))::numeric,
        1
    ) as late_rate_pct
from {{ ref('fct_orders') }}
where is_delivered
  and review_score is not null
  and delivery_days is not null
group by 1
