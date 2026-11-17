SELECT
    ticker,
    date,
    rounded_close AS price
FROM {{ source('raw', 'prices_daily') }}
