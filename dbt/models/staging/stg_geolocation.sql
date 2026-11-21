-- Collapse the raw geolocation extract to one row per zip prefix.
-- 1) drop exact duplicate coordinate rows
-- 2) trim, unaccent and title-case city names (e.g. 'são paulo' / 'sao paulo')
-- 3) average coordinates and take the modal city and state per zip

with deduplicated as (
    select distinct
        lpad(geolocation_zip_code_prefix::text, 5, '0') as geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        initcap(unaccent(btrim(geolocation_city))) as geolocation_city,
        upper(btrim(geolocation_state)) as geolocation_state
    from {{ source('raw', 'geolocation') }}
)

select
    geolocation_zip_code_prefix,
    avg(geolocation_lat)::numeric(9, 6) as geolocation_lat,
    avg(geolocation_lng)::numeric(9, 6) as geolocation_lng,
    mode() within group (order by geolocation_city) as geolocation_city,
    mode() within group (order by geolocation_state) as geolocation_state
from deduplicated
group by geolocation_zip_code_prefix
