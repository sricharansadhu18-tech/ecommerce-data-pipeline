-- Grain is (review_id, order_id). 789 review_ids are reused across
-- different orders with the same score and text; those rows are kept
-- because each order still has a review. Blank comments are set to null.

select
    review_id,
    order_id,
    review_score,
    nullif(btrim(review_comment_title), '') as review_comment_title,
    nullif(btrim(review_comment_message), '') as review_comment_message,
    review_creation_date::timestamp as review_creation_date,
    review_answer_timestamp::timestamp as review_answer_timestamp
from {{ source('raw', 'order_reviews') }}
