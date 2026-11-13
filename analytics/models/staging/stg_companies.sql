SELECT
    ticker,
    name,
    sector,
    industry,
    country,
    currency,
    market_cap,
    ttm_ebitda
FROM {{ source('raw', 'companies') }}
WHERE ticker IS NOT NULL
