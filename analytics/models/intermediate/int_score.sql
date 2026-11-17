/*
Global investment score (0-100) per company.
Each KPI is turned into a 0-100 score using its percentile rank across the universe
(100 = best), then combined with fixed weights. Missing KPIs score 0.
The trend score comes directly from int_trend.trend_score (already on a 0-100 scale).
*/

WITH latest_trend AS (
    SELECT ticker, trend_score
    FROM {{ ref('int_trend') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) = 1
),

relative AS (
    SELECT
        k.ticker,
        k.name,
        k.sector,
        k.industry,
        k.trailing_pe / NULLIF(MEDIAN(k.trailing_pe) OVER (PARTITION BY k.industry), 0) AS rel_trailing_pe,
        k.forward_pe  / NULLIF(MEDIAN(k.forward_pe)  OVER (PARTITION BY k.industry), 0) AS rel_forward_pe,
        t.trend_score,
        k.net_debt_to_ebitda_ratio,
        k.roic,
        k.fcf_to_net_income,
        k.eps_cagr_3y
    FROM {{ ref('int_kpis') }} AS k
    LEFT JOIN latest_trend AS t ON k.ticker = t.ticker
),

scores AS (
    SELECT
        *,
        -- Lower is better: sort DESC. NULLS FIRST so missing values get the lowest score
        100 * PERCENT_RANK() OVER (ORDER BY rel_trailing_pe DESC NULLS FIRST)           AS score_trailing_pe,
        100 * PERCENT_RANK() OVER (ORDER BY rel_forward_pe DESC NULLS FIRST)            AS score_forward_pe,
        ((100 * PERCENT_RANK() OVER (ORDER BY rel_trailing_pe DESC NULLS FIRST)) + (100 * PERCENT_RANK() OVER (ORDER BY rel_forward_pe DESC NULLS FIRST))) / 2 AS score_pe,
        100 * PERCENT_RANK() OVER (ORDER BY net_debt_to_ebitda_ratio DESC NULLS FIRST)  AS score_net_debt,
        -- Higher is better: sort ASC
        100 * PERCENT_RANK() OVER (ORDER BY roic ASC NULLS FIRST)                       AS score_roic,
        100 * PERCENT_RANK() OVER (ORDER BY fcf_to_net_income ASC NULLS FIRST)          AS score_earnings_quality,
        100 * PERCENT_RANK() OVER (ORDER BY eps_cagr_3y ASC NULLS FIRST)                AS score_growth,
        -- Already 0-100 from int_trend; missing price history scores 0
        COALESCE(trend_score, 0)                                                        AS score_trend
    FROM relative
)

SELECT
    ticker,
    name,
    sector,
    industry,
    ROUND(
          0.08 * score_trailing_pe
        + 0.08 * score_forward_pe
        + 0.14 * score_trend
        + 0.14 * score_net_debt
        + 0.14 * score_roic
        + 0.14 * score_earnings_quality
        + 0.14 * score_growth
    , 0) AS investment_score,
    ROUND(score_trailing_pe, 0)      AS score_trailing_pe,
    ROUND(score_forward_pe, 0)       AS score_forward_pe,
    ROUND(score_pe, 0)               AS score_pe,
    ROUND(score_trend, 0)            AS score_trend,
    ROUND(score_net_debt, 0)         AS score_net_debt,
    ROUND(score_roic, 0)             AS score_roic,
    ROUND(score_earnings_quality, 0) AS score_earnings_quality,
    ROUND(score_growth, 0)           AS score_growth
FROM scores