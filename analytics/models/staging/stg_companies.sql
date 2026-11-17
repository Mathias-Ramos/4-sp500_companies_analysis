SELECT
    ticker,
    name,
    sector,
    industry,
    country,
    currency
FROM {{ source('raw', 'companies') }}
WHERE ticker IS NOT NULL
