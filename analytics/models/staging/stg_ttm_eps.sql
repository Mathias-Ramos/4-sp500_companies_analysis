SELECT
    ticker,
    date,
    ttm_eps
FROM {{ source('raw', 'ttm_eps') }}
