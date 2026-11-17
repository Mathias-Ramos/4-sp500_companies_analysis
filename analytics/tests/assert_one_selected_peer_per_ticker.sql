/*
Exactly one peer row per selected company must be flagged as selected.
*/

WITH counts AS (
    SELECT
        ticker,
        COUNT_IF(is_selected) AS n_selected
    FROM {{ ref('mart_peers') }}
    GROUP BY ticker
)

SELECT *
FROM counts
WHERE n_selected <> 1
