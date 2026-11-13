SELECT
    ticker,
    date,
    total_debt,
    cash_and_equivalents,
    stockholders_equity,
    invested_capital,
    net_debt,
    total_assets,
    cash_and_short_term_investments
FROM {{ source('raw', 'balance_sheet') }}