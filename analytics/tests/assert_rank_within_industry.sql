/*
A company's rank within its industry can never exceed the industry size
(and must start at 1).
*/

SELECT *
FROM {{ ref('mart_score') }}
WHERE rank_in_industry > companies_in_industry
    OR rank_in_industry < 1
