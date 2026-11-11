SELECT
    ticker,
    period,
    "CURRENT" AS current_estimate,
    days_7_ago,
    days_30_ago,
    days_60_ago,
    days_90_ago,
    currency,
    methodology
FROM {{ source('raw', 'eps_trend') }}