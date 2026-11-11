SELECT
    ticker,
    date,
    total_debt,
    cash_and_equivalents,
    stockholders_equity
FROM {{ source('raw', 'balance_sheet') }}