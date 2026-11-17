/*
This model calculates the key valuation and profitability ratios for each company:
- Trailing and forward P/E ratios (from the latest valuation metrics) with industry averages
- Net Debt / EBITDA
- ROIC = NOPAT / invested capital, with NOPAT = EBIT * (1 - effective tax rate)
- Free cash flow and FCF / Net Income
- EPS CAGR over 3 years (NULL when either the starting or ending EPS is negative or zero)
*/

-- Only get the latest valuation metrics with a trailing P/E for each company
WITH latest_valuation AS (
    SELECT
        ticker,
        trailing_pe,
        forward_pe
    FROM {{ ref('stg_metrics') }}
    WHERE trailing_pe IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) = 1
)

,

-- Only get the latest balance sheet for each company
latest_bs AS (
    SELECT
        ticker,
        total_debt,
        cash_and_equivalents,
        stockholders_equity,
        invested_capital,
        net_debt
    FROM {{ ref('stg_balance_sheet') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) = 1
)

,

-- Only get the latest cashflows for each company
latest_cf AS (
    SELECT
        ticker,
        operating_cash_flow,
        capital_expenditure
    FROM {{ ref('stg_cashflow') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) = 1
)

,

-- Only get the latest income statement for each company
latest_is AS (
    SELECT
        ticker,
        ebitda,
        ebit,
        tax_provision,
        pretax_income,
        net_income,
        diluted_eps
    FROM {{ ref('stg_income_stmt') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) = 1
)

,

-- Only get the income statement from ~3 years ago (the row whose date is closest to the latest date minus 3 years, robust to missing fiscal years, ignoring rows with missing EPS) for each company
eps_3y_ago AS (
    SELECT
        ticker,
        diluted_eps
    FROM (
        SELECT
            i.ticker,
            i.diluted_eps,
            ROW_NUMBER() OVER (
                PARTITION BY i.ticker
                ORDER BY ABS(DATEDIFF('day', i.date, d.latest_date - INTERVAL '3 years')), i.date DESC
            ) AS rn
        FROM {{ ref('stg_income_stmt') }} AS i
        JOIN (
            SELECT ticker, MAX(date) AS latest_date
            FROM {{ ref('stg_income_stmt') }}
            GROUP BY ticker
        ) AS d
            ON i.ticker = d.ticker
        WHERE i.diluted_eps IS NOT NULL
    )
    WHERE rn = 1
)

-- Calculate the P/E ratio, forward P/E ratio, and net debt to EBITDA ratio for each company, along with the average P/E and forward P/E ratios for their respective industries
SELECT
    c.ticker,
    c.name,
    c.sector,
    c.industry,

    -- PRICE TO EARNINGS RATIOS:
    -- Using the median instead of the mean to avoid outliers skewing the average
    v.trailing_pe,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.trailing_pe) OVER (PARTITION BY c.industry),2) AS avg_industry_trail_pe,
    v.forward_pe,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.forward_pe) OVER (PARTITION BY c.industry),2) AS avg_industry_forw_pe,

    -- FINANCIAL STRENGTH: NET DEBT TO EBITDA RATIO:
    ROUND(
        COALESCE(
            bs.net_debt, 
            bs.total_debt - bs.cash_and_equivalents) / NULLIF(is_.ebitda, 0)  -- Net debt value is sometimes NULL
    , 2) AS net_debt_to_ebitda_ratio,

    -- RETURN ON INVESTED CAPITAL (ROIC): ROIC = NOPAT / invested capital, with NOPAT = EBIT * (1 - effective tax rate)
    ROUND(
        (is_.ebit * (1 - (is_.tax_provision / NULLIF(is_.pretax_income, 0)))) / NULLIF(bs.invested_capital, 0)
    , 2) AS roic,

    -- EARNINGS QUALITY: Free cash flow and FCF / Net Income
    ROUND((cf.operating_cash_flow + cf.capital_expenditure), 2) AS free_cash_flow,
    ROUND((cf.operating_cash_flow + cf.capital_expenditure) / NULLIF(is_.net_income, 0), 2) AS fcf_to_net_income,

    -- EARNINGS GROWTH: EPS CAGR over 3 years = (EPS_latest / EPS_3y_ago)^(1/3) - 1
    -- NULL when either EPS is negative or zero (CAGR is undefined)
    CASE
        WHEN is_.diluted_eps > 0 AND e3.diluted_eps > 0
        THEN ROUND(POWER(is_.diluted_eps / e3.diluted_eps, 1.0 / 3) - 1, 4)
    END AS eps_cagr_3y

FROM {{ ref('stg_companies') }} AS c
LEFT JOIN latest_valuation AS v
    ON c.ticker = v.ticker
LEFT JOIN latest_bs AS bs
    ON c.ticker = bs.ticker
LEFT JOIN latest_cf AS cf
    ON c.ticker = cf.ticker
LEFT JOIN latest_is AS is_
    ON c.ticker = is_.ticker
LEFT JOIN eps_3y_ago AS e3
    ON c.ticker = e3.ticker
