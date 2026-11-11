SELECT
    ticker,
    date,
    adj_close
FROM {{ source('raw', 'prices_weekly') }}