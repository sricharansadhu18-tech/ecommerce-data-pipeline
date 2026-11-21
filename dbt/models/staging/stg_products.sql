-- Clean product attributes and standardise category names.
-- The official Olist translation table covers 71 of 73 categories;
-- two Portuguese names are mapped here, and null categories become 'unknown'.
-- Source typo columns (lenght) are renamed.

with products as (
    select
        product_id,
        nullif(btrim(product_category_name), '') as product_category_name,
        product_name_lenght as product_name_length,
        product_description_lenght as product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    from {{ source('raw', 'products') }}
),

translations as (
    select
        product_category_name,
        product_category_name_english
    from {{ source('raw', 'product_category_translation') }}
),

missing_translations as (
    select *
    from (
        values
            ('portateis_cozinha_e_preparadores_de_alimentos', 'portable_kitchen_and_food_preparers'),
            ('pc_gamer', 'pc_gamer')
    ) as manual(product_category_name, product_category_name_english)
)

select
    p.product_id,
    p.product_category_name,
    coalesce(
        t.product_category_name_english,
        m.product_category_name_english,
        'unknown'
    ) as product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from products p
left join translations t
    on p.product_category_name = t.product_category_name
left join missing_translations m
    on p.product_category_name = m.product_category_name
