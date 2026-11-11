SELECT
    ticker,
    period,
    avg,
    low,
    high,
    number_of_analysts,
    year_ago_revenue,
    growth,
    currency
FROM {{ source('raw', 'revenue_estimate') }}