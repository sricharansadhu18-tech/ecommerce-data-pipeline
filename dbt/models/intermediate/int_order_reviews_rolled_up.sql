select
    order_id,
    (array_agg(review_score order by review_answer_timestamp desc nulls last, review_creation_date desc nulls last))[1] as review_score,
    avg(review_score)::numeric(5, 2) as avg_review_score,
    count(*) as review_count
from {{ ref('stg_order_reviews') }}
group by order_id
