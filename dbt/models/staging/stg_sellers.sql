select
    seller_id,
    lpad(seller_zip_code_prefix::text, 5, '0') as seller_zip_code_prefix,
    initcap(unaccent(btrim(seller_city))) as seller_city,
    upper(btrim(seller_state)) as seller_state
from {{ source('raw', 'sellers') }}
