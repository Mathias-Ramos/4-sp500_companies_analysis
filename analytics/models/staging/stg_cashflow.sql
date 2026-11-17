SELECT
    ticker,
    date,
    operating_cash_flow,
    capital_expenditure
FROM {{ source('raw', 'cashflow') }}