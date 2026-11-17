
SELECT
    k.ticker,
    k.name,
    k.sector,
    k.industry,
    k.trailing_pe,
    k.forward_pe,
    k.avg_industry_trail_pe,
    k.avg_industry_forw_pe,
    k.net_debt_to_ebitda_ratio,
    k.roic,
    k.free_cash_flow,
    k.fcf_to_net_income,
    k.eps_cagr_3y,
    s.investment_score AS score,
    RANK() OVER (PARTITION BY k.industry ORDER BY s.investment_score DESC NULLS LAST) AS rank_in_industry,
    COUNT(*) OVER (PARTITION BY k.industry)                                          AS companies_in_industry
FROM {{ ref('int_kpis') }} AS k
LEFT JOIN {{ ref('int_score') }} AS s
    ON k.ticker = s.ticker