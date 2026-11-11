SELECT
    ticker,
    pe,
    forward_pe,
    ebitda,
    sector,
    industry,
    currency,
    market_cap
FROM {{ source('raw', 'financials') }}