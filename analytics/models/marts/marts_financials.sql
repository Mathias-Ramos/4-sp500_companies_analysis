SELECT
    ticker,
    date,
    YEAR(date)                          AS fiscal_year,
    revenue,
    net_income,
    net_income / NULLIF(revenue, 0)     AS net_margin
FROM {{ ref('stg_income_stmt') }}