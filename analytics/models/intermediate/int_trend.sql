/*
This model calculates the 50-week simple moving average (SMA) for each stock ticker based on the daily adjusted closing prices.
It determines the trend (Bullish, Bearish, or Neutral) by comparing the close to the SMA, and computes a trend score (0-100):
- initial score
- + fixed bonus if the close is above the SMA (bullish)
- - fixed penalty for each consecutive bearish close (close below the previous close), floored at 0
- + bonus that grows the closer the close is to the SMA (a bounce is expected)
*/

{% set initial_score = 50 %}
{% set bullish_bonus = 30 %}
{% set bearish_penalty = 10 %}     -- per consecutive bearish close (10 in a row wipes the score)
{% set proximity_max_bonus = 20 %}
{% set proximity_band = 0.10 %}    -- bonus fades to 0 when price is 10% away from the SMA

WITH sma AS (
    SELECT
        ticker,
        date,
        price AS close,
        LAG(price) OVER (PARTITION BY ticker ORDER BY date) AS prev_close,
        ROUND(AVG(price) OVER (PARTITION BY ticker ORDER BY date RANGE BETWEEN 349 PRECEDING AND CURRENT ROW), 2) AS moving_avg_50w
    FROM {{ ref('stg_prices_daily') }}
)

-- A new group starts every time a close is NOT bearish, so counting
-- bearish closes inside a group gives the current consecutive streak.
, flagged AS (
    SELECT
        *,
        CASE WHEN close < prev_close THEN 1 ELSE 0 END AS is_bearish_close,
        SUM(CASE WHEN close < prev_close THEN 0 ELSE 1 END)
            OVER (PARTITION BY ticker ORDER BY date) AS streak_group
    FROM sma
)

, streaks AS (
    SELECT
        *,
        SUM(is_bearish_close) OVER (PARTITION BY ticker, streak_group ORDER BY date) AS consecutive_bearish_closes
    FROM flagged
)

SELECT
    ticker,
    date,
    close,
    moving_avg_50w,
    CASE WHEN close > moving_avg_50w THEN 'Bullish'
         WHEN close < moving_avg_50w THEN 'Bearish'
         ELSE 'Neutral'
    END AS trend,
    consecutive_bearish_closes,
    GREATEST(0,
          {{ initial_score }}
        + CASE WHEN close > moving_avg_50w THEN {{ bullish_bonus }} ELSE 0 END
        - {{ bearish_penalty }} * consecutive_bearish_closes
        + {{ proximity_max_bonus }} * GREATEST(0, 1 - ABS(close - moving_avg_50w) / NULLIF(moving_avg_50w, 0) / {{ proximity_band }})
    ) AS trend_score
FROM streaks