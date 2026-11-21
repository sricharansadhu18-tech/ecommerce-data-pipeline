select
    customer_id,
    customer_unique_id,
    lpad(customer_zip_code_prefix::text, 5, '0') as customer_zip_code_prefix,
    initcap(unaccent(btrim(customer_city))) as customer_city,
    upper(btrim(customer_state)) as customer_state
from {{ source('raw', 'customers') }}
