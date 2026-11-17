/*
The investment score must equal the weighted sum of its component scores
(within rounding tolerance: weighted error from rounding each component
is at most ~0.93, so 1.5 leaves a safety margin).
*/

SELECT *
FROM {{ ref('int_score') }}
WHERE ABS(
          0.08 * score_trailing_pe
        + 0.08 * score_forward_pe
        + 0.14 * score_trend
        + 0.14 * score_net_debt
        + 0.14 * score_roic
        + 0.14 * score_earnings_quality
        + 0.14 * score_growth
        - investment_score
    ) > 1.5
