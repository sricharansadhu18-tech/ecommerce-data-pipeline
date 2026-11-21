{{ config(materialized='table') }}

with bounds as (
    select
        min(order_date) as start_date,
        greatest(
            max(order_date),
            max(delivered_date),
            max(estimated_delivery_date)
        ) as end_date
    from {{ ref('stg_orders') }}
),

spine as (
    select generate_series(start_date, end_date, interval '1 day')::date as date_day
    from bounds
)

select
    to_char(date_day, 'YYYYMMDD')::int as date_key,
    date_day as date_day,
    extract(year from date_day)::int as year,
    extract(quarter from date_day)::int as quarter,
    extract(month from date_day)::int as month,
    to_char(date_day, 'Month') as month_name,
    extract(week from date_day)::int as iso_week,
    extract(isodow from date_day)::int as iso_dow,
    to_char(date_day, 'Day') as day_name,
    extract(day from date_day)::int as day_of_month,
    (extract(isodow from date_day) >= 6) as is_weekend,
    to_char(date_day, 'YYYY-MM') as year_month
from spine
