SELECT
    ticker,
    period,
    avg,
    low,
    high,
    year_ago_eps,
    number_of_analysts,
    growth,
    currency,
    methodology
FROM {{ source('raw', 'earnings_estimate') }}