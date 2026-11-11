SELECT
    ticker,
    period,
    up_last7days AS up_last_7_days,
    up_last30days AS up_last_30_days,
    down_last30days AS down_last_30_days,
    down_last7_days AS down_last_7_days,
    currency,
    methodology
FROM {{ source('raw', 'eps_revisions') }}