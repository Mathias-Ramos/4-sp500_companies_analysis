SELECT
    ticker,
    name,
    sector,
    industry
FROM {{ source('raw', 'companies') }}
WHERE ticker IS NOT NULL