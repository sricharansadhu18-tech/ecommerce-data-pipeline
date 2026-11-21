select
    md5(product_id) as product_key,
    product_id,
    product_category_name,
    product_category_name_english,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
from {{ ref('stg_products') }}
