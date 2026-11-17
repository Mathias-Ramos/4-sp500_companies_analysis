SELECT
    ticker,
    date,
    revenue,
    ebit,
    ebitda,
    tax_provision,
    pretax_income,
    net_income,
    diluted_eps
FROM {{ source('raw', 'income_stmt') }}