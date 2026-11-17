SELECT
    ticker,
    date,
    market_cap,
    enterprise_value,
    trailing_pe,
    forward_pe,
    peg_ratio,
    price_sales,
    price_book,
    ev_revenue,
    ev_ebitda
FROM {{ source('raw', 'metrics') }}
