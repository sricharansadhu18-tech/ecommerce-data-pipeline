-- Sample business questions against the marts schema (PostgreSQL).
-- Run after a successful Airflow / dbt build.

-- 1) Monthly payment volume
select
    year_month,
    order_count,
    payment_volume,
    avg_order_value
from marts.mart_monthly_revenue
order by year_month;

-- 2) Top categories by merchandise revenue
select *
from marts.mart_category_performance
order by merchandise_revenue desc
limit 10;

-- 3) Late delivery rate by state
select *
from marts.mart_late_delivery_by_state
order by late_rate_pct desc;

-- 4) On-time vs late review scores
select *
from marts.mart_delivery_reviews
order by delivery;

-- 5) Headline: late deliveries vs review score (from fct_orders)
select
    case when is_late then 'Late' else 'On time' end as delivery,
    count(*) as orders,
    round(avg(review_score)::numeric, 2) as avg_review
from marts.fct_orders
where is_delivered
  and review_score is not null
group by 1
order by 1;
