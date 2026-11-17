/*
The low estimate can never exceed the high estimate (EPS and revenue).
NULL bounds are ignored (the comparison yields NULL, not TRUE).

severity: warn because the root cause is the upstream yfinance data
(observed on 2026-11-17: KKR +1q, TDG 0y with eps_low > eps_high),
and these columns are not used in any downstream scoring model.
*/

{{ config(severity='warn') }}

SELECT *
FROM {{ ref('stg_analyst_estimates') }}
WHERE eps_low > eps_high
    OR revenue_low > revenue_high
