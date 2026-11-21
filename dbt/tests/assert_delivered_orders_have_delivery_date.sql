{{ config(severity="warn") }}
-- Real data-quality check: a small number of Olist orders are marked
-- delivered but have no order_delivered_customer_date.
select order_id, order_status, delivered_date
from {{ ref('fct_orders') }}
where is_delivered
  and delivered_date is null
