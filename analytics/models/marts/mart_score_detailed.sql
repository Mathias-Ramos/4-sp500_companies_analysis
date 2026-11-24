WITH unpivot AS (
    SELECT
        ticker,
        'P/E' AS score_cat,
        score_pe AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'Net debt' AS score_cat,
        score_net_debt AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'ROIC' AS score_cat,
        score_roic AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'Earnings' AS score_cat,
        score_earnings_quality AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'Growth' AS score_cat,
        score_growth AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'Technical' AS score_cat,
        score_trend AS score
    FROM {{ref ('int_score')}}

    UNION ALL

    SELECT
        ticker,
        'General' AS score_cat,
        investment_score AS score
    FROM {{ref ('int_score')}}
)


SELECT
    ticker,
    score_cat,
    score
FROM unpivot
ORDER BY ticker, score_cat